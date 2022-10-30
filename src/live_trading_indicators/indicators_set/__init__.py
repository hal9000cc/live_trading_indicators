import logging
import datetime as dt
import importlib
from enum import Enum
from ..config import config_load
from ..cast_input_params import *
from ..exceptions import *
from ..timeframe import *
from .. import datasources


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
        self.time_end = cast_time(time_end)

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

        self.reset()

        # self.set_time_interval(time_begin, time_end)

    def init_log(self):

        if not self.config['print_log']: return

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            handlers=[logging.StreamHandler()])

    def check_call_time_intervals_fixed(self, time_begin, time_end):

        if time_begin is None:
            time_begin = self.time_begin

        if time_end is None:
            time_end = self.time_end

        if time_begin < self.time_begin or time_end > self.time_end:
            raise LTIExceptionOutOfThePeriod()

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
            self.reset()

        if self.time_end is None or self.time_end < time_end:
            self.time_end = time_end
            self.reset()

        return time_begin, time_end

    def check_call_time_intervals_live(self, time_begin, time_end, timeframe):

        if time_begin is None:
            time_begin = self.time_begin

        if time_end is not None:
            raise LTIExceptionBadTimeParameter('Time end cannot be set in live mode')

        now = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT)
        if time_begin > now:
            raise LTIExceptionBadTimeParameter('Time begin later of the now time')

        time_end = timeframe.begin_of_tf(dt.datetime.utcnow())
        if self.time_end is None or self.time_end < time_end:
            self.time_end = time_end
            self.reset(timeframe)

        if self.with_incomplete_bar:
            self.reset()

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

    def get_bar_data(self, symbol, timeframe):

        time_start = timeframe.begin_of_tf(self.time_begin)

        if self.interval_mode == IntervalMode.live:
            time_end = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT)
        else:
            time_end = timeframe.begin_of_tf(self.time_end)

        bar_data = self.source_data.get_bar_data(symbol, timeframe, time_start, time_end)

        if self.interval_mode == IntervalMode.live:
            index_start = bar_data.index_from_time64(time_start)
            index_end = bar_data.index_from_time64(time_end)
            bar_data = bar_data[index_start: index_end + 1 if bar_data.close[index_end] else index_end]
        else:
            bar_data = bar_data[time_start : time_end + timeframe.value]

        self.check_bar_data(bar_data, symbol, self.time_begin, self.time_end)

        if self.config['restore_empty_bars']:
            bar_data.restore_bar_data()
        return bar_data

    def check_bar_data(self, bar_data, symbol, date_begin, date_end):

        if self.config['endpoints_required']:
            if len(bar_data) == 0:
                raise LTIExceptionSourceDataNotFound(symbol, date_begin)
            if bar_data.close[0] == 0:
                raise LTIExceptionSourceDataNotFound(symbol, date_begin)
            if bar_data.close[-1] == 0:
                raise LTIExceptionSourceDataNotFound(symbol, date_end)

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

    def get_indicator_out(self, symbols, timeframe, time_begin, time_end, **kwargs):

        time_begin, time_end = self.indicators.check_call_time_intervals(time_begin, time_end, timeframe)

        out = self.indicators.get_out_from_cache(self.indicator_name, symbols, timeframe, kwargs)

        if out is None:

            out = self.indicator_module.get_indicator_out(self.indicators, symbols, timeframe, **kwargs)
            out.read_only = True

            if time_end == out.time[-1]:
                self.indicators.put_out_to_cache(self.indicator_name, symbols, timeframe, kwargs, out)

        return out[time_begin: time_end + out.timeframe.timedelta64() if time_end else None]

    def __call__(self, symbols, timeframe, time_begin=None, time_end=None, **kwargs):

        use_time_begin, use_time_end = cast_time(time_begin), cast_time(time_end)
        use_timeframe = Timeframe.cast(timeframe)

        if use_time_begin is not None and use_time_end is not None and use_time_begin > use_time_end:
            raise LTIExceptionTimeBeginLaterTimeEnd(use_time_begin, use_time_end)

        return self.get_indicator_out(symbols, use_timeframe, use_time_begin, use_time_end, **kwargs)

    def __del__(self):
        self.indicators = None

