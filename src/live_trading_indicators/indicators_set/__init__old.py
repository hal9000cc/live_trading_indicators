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
    float = 3


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

    def __init__(self, datasource, time_begin=None, time_end=None, **config_mod):

        self.indicators = {}

        self.config = config_load() | config_mod
        self.init_log()

        datasource_type = type(datasource)
        if datasource_type == str:
            datasource_module = importlib.import_module(f'..datasources.{datasource}', __package__)
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
                self.interval_mode = Indicators.IntervalMode.fixed
            else:
                self.interval_mode = Indicators.IntervalMode.live
        else:
            if self.time_end is None:
                self.interval_mode = Indicators.IntervalMode.float
            else:
                raise LTIBadTimeParameter(self.time_begin)

        self.reset()

    def init_log(self):

        if not self.config['print_log']:
            return

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            handlers=[logging.StreamHandler()])

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

    def reset(self):
        self.cache = {}

    @staticmethod
    def key_from_args(indicator, symmbols, timeframe, kwargs):
        return symmbols, timeframe, tuple(kwargs.items())

    def get_bar_data(self, symbol, timeframe, time_begin, time_end):

        bar_data = self.source_data.get_bar_data(symbol, timeframe, time_begin, time_end)

        ix_last_bar = bar_data.index_from_time(time_end)

        if ix_last_bar < len(bar_data) - 1:
            bar_data = bar_data[:ix_last_bar + 1]

        self.check_bar_data(bar_data, symbol, time_begin, time_end)

        if self.config['restore_empty_bars']:
            bar_data.restore_bar_data()
        return bar_data

    def check_bar_data(self, bar_data, symbol, date_begin, date_end):

        if self.config['endpoints_required']:
            if len(bar_data) == 0:
                raise LTISourceDataNotFound(symbol, date_begin)
            if bar_data.close[0] == 0:
                raise LTISourceDataNotFound(symbol, date_begin)
            if bar_data.close[-1] == 0:
                raise LTISourceDataNotFound(symbol, date_end)

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
            raise LTIExceptionIndicatorNotFound(indicator_name)

    def get_indicator_out(self, symbols, timeframe, time_begin, time_end, **kwargs):

        self.indicators.check_call_time_intervals(time_begin, time_end)

        out = self.indicators.get_out_from_cache(self.indicator_name, symbols, timeframe, kwargs)

        if out is None:
            out = self.indicator_module.get_indicator_out(self.indicators, symbols, timeframe, time_begin, time_end, **kwargs)
            out.read_only = True
            self.indicators.put_out_to_cache(self.indicator_name, symbols, timeframe, kwargs, out)

        return out[time_begin: time_end + out.timeframe.timedelta() if time_end else None]

    def __call__(self, symbols, timeframe, time_begin, time_end, **kwargs):
        return self.get_indicator_out(symbols, Timeframe.cast(timeframe), cast_time(time_begin), cast_time(time_end), **kwargs)

    def __del__(self):
        del self.indicators

