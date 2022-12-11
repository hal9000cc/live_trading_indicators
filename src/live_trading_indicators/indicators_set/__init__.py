import logging
import logging.config
import os
import os.path as path
import importlib
from enum import Enum
from abc import ABC, abstractmethod
from ..config import config_load, get_logging_config
from ..cast_input_params import *
from ..exceptions import *
from ..timeframe import *
from .. import datasources
from ..indicator_data import OHLCV_data
from ..constants import PRICE_TYPE, VOLUME_TYPE, TIME_TYPE, TIME_UNITS_IN_ONE_SECOND

logger = logging.getLogger(__name__)

class IndicatorsMode(Enum):
    fixed = 1
    live = 2
    flex = 3
    offline = 4


class Indicators:
    """
    Pool af indicators.

    Indicators(datasource, date_begin, date_end, **config_mod)

        datasource:
            Source of trading quotes. The name of the module from datasources or the module itself.

        date_begin, date_end:
            Start and end dates of the indicator calculation interval. Dates are set inclusive.
            Dates can be set as date, datetime, datetime64, string ISO 8601, or as an integer of the form YYYYMMDD.

        config_mod:
            Configuration modification.
    """

    def __init__(self, datasource, time_begin=None, time_end=None, with_incomplete_bar=False, symbol=None,
                 exchange_params=None,
                 **config_mod):

        self.config = config_load() | config_mod

        self.init_log()

        self.indicators = {}
        self.cache = {}

        self.with_incomplete_bar = with_incomplete_bar

        self.offline_timeframe = None
        self.offline_symbol = symbol
        self.time_begin = None
        self.time_end = None
        self.source_data = None
        self.indicators_mode = None

        datasource_type = type(datasource)
        if datasource_type == str:

            try:
                datasource_module = importlib.import_module(f'..datasources.{datasource.split(".")[0]}', __package__)
            except ModuleNotFoundError as error:
                raise LTIExceptionBadDatasource(datasource) from error

            self.init_online_source(datasource_module, datasource, exchange_params, time_begin, time_end)

        elif datasource_type.__name__ == 'module':
            self.init_online_source(datasource, time_begin, time_end)
        elif datasource_type.__name__ == 'DataFrame':
            self.init_offline_source(datasource, time_begin, time_end, with_incomplete_bar)
        else:
            raise LTIExceptionBadDatasource(datasource)

    def init_offline_source(self, datasource, time_begin, time_end, with_incomplete_bar):

        if time_begin or time_end or with_incomplete_bar:
            LTIExceptionBadParameterValue('cannot specify time_begin, time_end, with_incomplete_bar in offline mode')

        if datasource.time.count() < 2:
            LTIExceptionBadDatasource('dataframe is empty')

        time_series = datasource.time.to_numpy(dtype=TIME_TYPE)

        self.offline_timeframe = Timeframe.cast(int((time_series[1] - time_series[0]).astype(np.int64)))
        self.time_begin = time_series[0]
        self.time_end = Timeframe.begin_of_tf(self.offline_timeframe, time_series[-1])

        not_found_columns = {'time', 'open', 'high', 'low', 'close', 'volume'} - set(datasource.columns)
        if not_found_columns:
            raise LTIExceptionBadOfflineDataSource(
                f'columns not found: {not_found_columns}'
            )

        self.source_data = OHLCV_data({
            'symbol': self.offline_symbol,
            'timeframe': self.offline_timeframe,
            'time': time_series,
            'open': datasource.open.to_numpy(dtype=PRICE_TYPE),
            'high': datasource.high.to_numpy(dtype=PRICE_TYPE),
            'low': datasource.low.to_numpy(dtype=PRICE_TYPE),
            'close': datasource.close.to_numpy(dtype=PRICE_TYPE),
            'volume': datasource.volume.to_numpy(dtype=VOLUME_TYPE)
        })

        self.check_bar_data(self.source_data)

        if self.config['restore_empty_bars']:
            self.source_data.restore_bar_data()

        self.source_data.read_only = True

        self.indicators_mode = IndicatorsMode.offline

    def init_online_source(self, datasource_module, datasource_name, exchange_params, time_begin, time_end):

        self.datasource_name = datasource_module.datasource_name()
        datasource_module.init(self.config, datasource_name, exchange_params)
        self.source_data = datasources.SourceData(datasource_module, self.config)

        self.time_begin = cast_time(time_begin)
        self.time_end = cast_time(time_end, True)

        if self.time_begin is not None:
            if self.time_end is not None:

                if self.time_begin > self.time_end:
                    raise LTIExceptionTimeBeginLaterTimeEnd(self.time_begin, self.time_end)

                self.indicators_mode = IndicatorsMode.fixed

            else:
                self.indicators_mode = IndicatorsMode.live
        else:
            if self.time_end is None:
                self.indicators_mode = IndicatorsMode.flex
            else:
                raise LTIExceptionBadTimeParameter(self.time_begin)

    def init_log(self):
        logging.config.dictConfig(get_logging_config(self.config))

    def __del__(self):
        del self.source_data
        self.indicators = None

    def __str__(self):

        str_time_begin = self.time_begin if self.time_begin is None else self.time_begin.astype("datetime64[m]")
        str_time_end = self.time_begin if self.time_end is None else self.time_end.astype("datetime64[m]")

        str_list = [f'<Indicators> source: {self.datasource_name}',
                    f'work period = {str_time_begin} : {str_time_end}']

        return '\n'.join(str_list)

    def __repr__(self):
        return self.__str__()

    def check_call_time_intervals_fixed(self, time_begin, time_end):

        if time_begin is None:
            time_begin = self.time_begin

        if time_end is None:
            time_end = self.time_end

        return time_begin, time_end

    def check_call_time_intervals_flex(self, time_begin, time_end):

        if time_begin is None:
            raise LTIExceptionBadTimeParameter('No time begin')

        if time_end is None:
            raise LTIExceptionBadTimeParameter('No time end')

        if time_begin > time_end:
            raise LTIExceptionTimeBeginLaterTimeEnd(time_begin, time_end)

        if self.time_begin is None or self.time_begin > time_begin:
            self.time_begin = time_begin

        if self.time_end is None or self.time_end < time_end:
            self.time_end = time_end

        return time_begin, time_end

    def check_call_time_intervals_live(self, time_begin, time_end, timeframe):

        if time_begin is None:
            time_begin = self.time_begin

        if time_end is not None:
            raise LTIExceptionBadTimeParameter('Time end cannot be set in live mode')

        now = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT)
        if time_begin > now:
            raise LTIExceptionBadTimeParameter('Time begin later of the now time')

        time_end = timeframe.begin_of_tf(now) + TIME_UNITS_IN_ONE_DAY
        self.time_end = time_end

        return time_begin, time_end

    def check_call_time_intervals(self, time_begin, time_end, timeframe):

        match self.indicators_mode:
            case IndicatorsMode.fixed:
                return self.check_call_time_intervals_fixed(time_begin, time_end)
            case IndicatorsMode.flex:
                return self.check_call_time_intervals_flex(time_begin, time_end)
            case IndicatorsMode.live:
                return self.check_call_time_intervals_live(time_begin, time_end, timeframe)
            case IndicatorsMode.offline:
                return self.check_call_time_intervals_fixed(time_begin, time_end)

        raise NotImplementedError(self.indicators_mode)

    def __getattr__(self, item):
        return self.get_indicator(item)

    def get_indicator(self, indicator_name):

        indicator_proxy = self.indicators.get(indicator_name)
        if indicator_proxy is None:

            if self.indicators_mode == IndicatorsMode.offline:
                indicator_proxy = IndicatorProxyOffline(indicator_name, self)
            else:
                indicator_proxy = IndicatorProxyOnline(indicator_name, self)

            self.indicators[indicator_name] = indicator_proxy

        return indicator_proxy

    def get_out_from_cache(self, indicator, symbols, timeframe, kwargs):
        key = self.key_from_args(indicator, symbols, timeframe, kwargs)
        return self.cache.get(key)

    def put_out_to_cache(self, indicator, symbols, timeframe, kwargs, out):
        key = self.key_from_args(indicator, symbols, timeframe, kwargs)
        self.cache[key] = out

    def get_indicator_out_valid(self, indicator_name, symbols, timeframe, indicator_kwargs, time_begin, time_end):

        if time_begin < self.time_begin:
            return None, None

        out = self.get_out_from_cache(indicator_name, symbols, timeframe, indicator_kwargs)

        if out is None:
            return None, None

        if out.first_bar_time > timeframe.begin_of_tf(self.time_begin):
            return None, None

        if out.end_bar_time + timeframe.value <= time_end:
            return None, out

        return out, None

    def get_indicator_out_cached(self, indicator_name, indicator_module, symbols, timeframe, indicator_kwargs,
                                 time_begin, time_end):

        out_valid, out_for_grow = self.get_indicator_out_valid(indicator_name, symbols, timeframe,
                                                               indicator_kwargs, time_begin, time_end)
        if out_valid is None:
            out_valid = indicator_module.get_indicator_out(self, symbols, timeframe, out_for_grow, **indicator_kwargs)
            self.put_out_to_cache(indicator_name, symbols, timeframe, indicator_kwargs, out_valid)

        if self.indicators_mode != IndicatorsMode.live and self.indicators_mode != IndicatorsMode.offline:
            if time_begin < out_valid.time[0] or out_valid.time[-1] + timeframe.value < time_end:
                raise LTIExceptionOutOfThePeriod()

        return out_valid[time_begin: time_end + timeframe.value]

    def get_indicator_out(self, indicator_name, indicator_module, symbols, timeframe, indicator_kwargs, time_begin,
                          time_end):

        use_time_begin, use_time_end = self.check_call_time_intervals(time_begin, time_end, timeframe)

        no_cached = hasattr(indicator_module, 'no_cached') and indicator_module.no_cached

        if no_cached:
            out = indicator_module.get_indicator_out(self, symbols, timeframe, use_time_begin, use_time_end,
                                                     **indicator_kwargs)
        else:
            out = self.get_indicator_out_cached(indicator_name, indicator_module, symbols, timeframe, indicator_kwargs,
                                                use_time_begin, use_time_end)

        return out

    def reset(self, timeframe=None):

        if timeframe is None:
            self.cache = {}
            return

        for key in tuple(self.cache.keys()):
            key_timeframe = key[1]
            assert isinstance(key_timeframe, Timeframe)
            if key_timeframe == timeframe:
                self.cache.pop(key)

    @staticmethod
    def key_from_args(indicator, symbols, timeframe, kwargs):
        return indicator, symbols, timeframe, tuple(kwargs.items())

    def get_bar_data(self, symbol, timeframe, bar_for_grow=None):

        if self.indicators_mode == IndicatorsMode.offline:
            return self.get_bar_data_offline()  # from pandas

        return self.get_bar_data_online(symbol, timeframe, bar_for_grow)

    def get_bar_data_offline(self):
        return self.source_data

    def get_bar_data_online(self, symbol, timeframe, bar_for_grow):

        time_start_d = np.datetime64(self.time_begin, 'D')
        time_end = timeframe.begin_of_tf(self.time_end)

        if bar_for_grow is None or len(bar_for_grow) < 2:
            bar_data = self.source_data.get_bar_data(symbol, timeframe, time_start_d, time_end)
        else:

            time_start_last_day_d = np.datetime64(bar_for_grow.time[-1], 'D')
            time_start_last_day = np.datetime64(time_start_last_day_d, TIME_TYPE_UNIT)

            new_day_data = self.source_data.get_bar_data(symbol, timeframe,
                                                         time_start_last_day_d, time_end,
                                                         bar_for_grow[time_start_last_day:])

            if bar_for_grow.time[0] == time_start_last_day:
                bar_data = new_day_data
            else:
                bar_data = bar_for_grow[:time_start_last_day] + new_day_data

        if bar_data.is_live:
            time_end = bar_data.time[-1] + (timeframe.value if self.with_incomplete_bar else -1)
            bar_data = bar_data[: time_end + timeframe.value]

        self.check_bar_data(bar_data)

        if self.config['restore_empty_bars']:
            bar_data.restore_bar_data()

        return bar_data

    def check_bar_data(self, bar_data):

        empty_bars_count, empty_bars_fraction, empty_bars_consecutive = None, None, None

        if self.config['endpoints_required']:
            if len(bar_data) == 0:
                raise LTIExceptionSourceDataNotFound(bar_data.symbol)
            if bar_data.close[0] == 0:
                raise LTIExceptionSourceDataNotFound(bar_data.symbol, bar_data.time[0])
            if bar_data.close[-1] == 0:
                raise LTIExceptionSourceDataNotFound(bar_data.symbol, bar_data.close[-1])

        max_empty_bars_fraction, max_empty_bars_consecutive = self.config['max_empty_bars_fraction'], self.config[
            'max_empty_bars_consecutive']
        if max_empty_bars_fraction is not None or max_empty_bars_consecutive is not None:

            empty_bars_count, empty_bars_fraction, empty_bars_consecutive = bar_data.get_skips()
            bar_data.data |= {
                'empty_bars_count': empty_bars_count,
                'empty_bars_fraction': empty_bars_fraction,
                'empty_bars_consecutive': empty_bars_consecutive
            }
            if (empty_bars_fraction is not None and empty_bars_fraction > self.config['max_empty_bars_fraction']) \
                    or (empty_bars_consecutive is not None and empty_bars_consecutive > max_empty_bars_consecutive):
                raise LTIExceptionTooManyEmptyBars(self.datasource_name,
                                                   bar_data.symbol,
                                                   bar_data.timeframe,
                                                   bar_data.first_bar_time,
                                                   bar_data.end_bar_time,
                                                   empty_bars_fraction,
                                                   empty_bars_consecutive)

        return empty_bars_count, empty_bars_fraction, empty_bars_consecutive


class IndicatorProxy(ABC):

    def __init__(self, indicator_name, indicators):

        self.indicator_name = indicator_name

        try:
            self.indicator_module = importlib.import_module(f'.{indicator_name}', __package__)
            self.indicators = indicators
        except ModuleNotFoundError as error:
            if error.name.split('.')[-1] == indicator_name:
                raise LTIExceptionIndicatorNotFound(indicator_name) from error
            raise

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def full_data(self, symbols, timeframe, **kwargs):

        time_begin = np.datetime64(np.datetime64(self.indicators.time_begin, 'D'), TIME_TYPE_UNIT)
        time_end = np.datetime64(np.datetime64(self.indicators.time_end, 'D') + 1, TIME_TYPE_UNIT) - 1

        return self.indicators.get_indicator_out(self.indicator_name, self.indicator_module, symbols, timeframe,
                                                 kwargs, time_begin, time_end)


class IndicatorProxyOnline(IndicatorProxy):

    def __call__(self, symbols, timeframe, time_begin=None, time_end=None, **kwargs):
        use_time_begin, use_time_end = cast_time(time_begin), cast_time(time_end, True)
        use_timeframe = Timeframe.cast(timeframe)

        if use_time_begin is not None and use_time_end is not None and use_time_begin > use_time_end:
            raise LTIExceptionTimeBeginLaterTimeEnd(use_time_begin, use_time_end)

        return self.indicators.get_indicator_out(self.indicator_name, self.indicator_module, symbols, use_timeframe,
                                                 kwargs, use_time_begin, use_time_end)


class IndicatorProxyOffline(IndicatorProxy):

    def __call__(self, time_begin=None, time_end=None, **kwargs):
        use_time_begin, use_time_end = cast_time(time_begin), cast_time(time_end, True)

        return self.indicators.get_indicator_out(self.indicator_name, self.indicator_module, None,
                                                 self.indicators.offline_timeframe,
                                                 kwargs, time_begin, time_end)


def helo_append(help_list, doc_str):
    help_list.append(f'- {doc_str}')


def help(mode=0):
    import os.path as path
    import glob

    class Help:

        def __init__(self, content):
            self.content = content

        def __str__(self):
            return self.content

        def __repr__(self):
            return self.content

    indicator_modules_path = path.split(__file__)[0]

    file_indicators = [path.basename(file_name) for file_name in glob.glob(path.join(indicator_modules_path, '*.py'))]
    file_indicators.sort()

    help_list = []
    for file in file_indicators:
        module_name = path.splitext(file)[0]
        if module_name[0] != '_':
            module = importlib.import_module(f'.{module_name}', __package__)
            if module.__doc__:
                if mode == 0:
                    helo_append(help_list, module.__doc__)
                else:
                    doc = module.__doc__.splitlines()
                    first_line = f'{doc[0]} - {doc[1]}'
                    doc.pop(0)
                    doc[0] = first_line
                    helo_append(help_list, '\n'.join(doc))
            else:
                help_list.append(f'{module_name}(?)')

    return Help('\n'.join(help_list))
