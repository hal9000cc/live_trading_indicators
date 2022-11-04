import logging
import datetime as dt
import importlib
from enum import Enum
from ..config import config_load
from ..cast_input_params import *
from ..exceptions import *
from ..timeframe import *
from .. import datasources
from ..indicator_data import OHLCV_data


class IntervalMode(Enum):
    fixed = 1
    live = 2
    flex = 3


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

    def __init__(self, datasource, time_begin=None, time_end=None, with_incomplete_bar=False, **config_mod):

        self.indicators = {}
        self.cache = {}

        self.config = config_load() | config_mod
        self.init_log()

        self.with_incomplete_bar = with_incomplete_bar

        datasource_type = type(datasource)
        if datasource_type == str:
            try:
                datasource_module = importlib.import_module(f'..datasources.{datasource}', __package__)
            except ModuleNotFoundError as error:
                raise LTIExceptionBadDatasource(datasource) from error
        elif datasource_type.__name__ == 'module':
            datasource_module = datasource
        else:
            raise LTIExceptionBadDatasource(datasource)

        self.datasource_name = datasource_module.datasource_name()
        datasource_module.init(self.config)
        self.source_data = datasources.SourceData(datasource_module, self.config)

        self.time_begin = cast_time(time_begin)
        self.time_end = cast_time(time_end, True)

        if self.time_begin is not None:
            if self.time_end is not None:

                if self.time_begin > self.time_end:
                    raise LTIExceptionTimeBeginLaterTimeEnd(self.time_begin, self.time_end)

                self.interval_mode = IntervalMode.fixed

            else:
                self.interval_mode = IntervalMode.live
        else:
            if self.time_end is None:
                self.interval_mode = IntervalMode.flex
            else:
                raise LTIExceptionBadTimeParameter(self.time_begin)

    def init_log(self):

        if not self.config['print_log']:
            return

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            handlers=[logging.StreamHandler()])

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

        if self.interval_mode == IntervalMode.fixed:
            return self.check_call_time_intervals_fixed(time_begin, time_end)
        if self.interval_mode == IntervalMode.flex:
            return self.check_call_time_intervals_flex(time_begin, time_end)
        if self.interval_mode == IntervalMode.live:
            return self.check_call_time_intervals_live(time_begin, time_end, timeframe)
        raise NotImplementedError(self.interval_mode)

    def __getattr__(self, item):
        return self.get_indicator(item)

    def get_indicator(self, indicator_name):

        indicator_proxy = self.indicators.get(indicator_name)
        if indicator_proxy is None:
            indicator_proxy = IndicatorProxy(indicator_name, self)
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

    def get_indicator_out(self, indicator_name, indicator_module, symbols, timeframe, indicator_kwargs, time_begin, time_end):

        use_time_begin, use_time_end = self.check_call_time_intervals(time_begin, time_end, timeframe)

        out_valid, out_for_grow = self.get_indicator_out_valid(indicator_name, symbols, timeframe,
                                                                      indicator_kwargs, use_time_begin, use_time_end)
        if out_valid is None:
            out_valid = indicator_module.get_indicator_out(self, symbols, timeframe, out_for_grow, **indicator_kwargs)
            self.put_out_to_cache(indicator_name, symbols, timeframe, indicator_kwargs, out_valid)

        if self.interval_mode != IntervalMode.live:
            if use_time_begin < out_valid.time[0] or out_valid.time[-1] + timeframe.value < use_time_end:
                raise LTIExceptionOutOfThePeriod()

        return out_valid[use_time_begin: use_time_end + timeframe.value]

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
        return symbols, timeframe, tuple(kwargs.items())

    def get_bar_data(self, symbol, timeframe, bar_for_grow=None):

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


class IndicatorProxy:

    def __init__(self, indicator_name, indicators):

        self.indicator_name = indicator_name

        try:
            self.indicator_module = importlib.import_module(f'.{indicator_name}', __package__)
            self.indicators = indicators
        except ModuleNotFoundError as error:
            if error.name.split('.')[-1] == indicator_name:
                raise LTIExceptionIndicatorNotFound(indicator_name) from error
            raise

    def __call__(self, symbols, timeframe, time_begin=None, time_end=None, **kwargs):

        use_time_begin, use_time_end = cast_time(time_begin), cast_time(time_end, True)
        use_timeframe = Timeframe.cast(timeframe)

        if use_time_begin is not None and use_time_end is not None and use_time_begin > use_time_end:
            raise LTIExceptionTimeBeginLaterTimeEnd(use_time_begin, use_time_end)

        return self.indicators.get_indicator_out(self.indicator_name, self.indicator_module, symbols, use_timeframe,
                                                 kwargs, use_time_begin, use_time_end)

    def full_data(self, symbols, timeframe,  **kwargs):

        time_begin = np.datetime64(np.datetime64(self.indicators.time_begin, 'D'), TIME_TYPE_UNIT)
        time_end = np.datetime64(np.datetime64(self.indicators.time_end, 'D') + 1, TIME_TYPE_UNIT) - 1

        return self.indicators.get_indicator_out(self.indicator_name, self.indicator_module, symbols, timeframe,
                                                 kwargs, time_begin, time_end)

    def __del__(self):
        self.indicators = None

