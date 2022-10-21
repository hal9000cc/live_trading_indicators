import logging
import datetime as dt
import importlib
from ..common import *
from ..exceptions import *
from .. import datasources


class Indicators:
    """
    Pool af indicators.

    Indicators(datasource, date_begin, date_end, **config_mod)

        datasource:
            Source of trading quotes. The name of the module from datasources or the module itself.

        date_begin, date_end:
            Start and end dates of the indicator calculation interval. Dates are set inclusive. Dates can be set as date, datetime, datetime64, or as an integer of the form YYYYMMDD.

        config_mod:
            Configuration modification.
    """
    def __init__(self, datasource, date_begin=None, date_end=None, **config_mod):

        self.indicators = {}

        self.config = config_load() | config_mod
        self.init_log()

        datasource_type = type(datasource)
        if datasource_type == str:
            datasource_module = importlib.import_module(f'..datasources.{datasource}', __package__)
        elif datasource_type.__name__ == 'module':
            datasource_module = datasource
        else:
            raise TypeError('Bad type of datasource')

        self.datasource_name = datasource_module.datasource_name()
        datasource_module.init(self.config)
        self.source_data = datasources.SourceData(datasource_module, self.config)

        self.date_begin = param_time(date_begin, False).date() if date_begin is not None else None
        self.date_end = param_time(date_end, True).date() if date_end is not None else None
        self.fix_date_begin = self.date_begin is not None
        self.fix_date_end = self.date_end is not None

        self.reset()

        #self.set_time_interval(time_begin, time_end)

    def init_log(self):

        if not self.config['print_log']: return

        logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()])

    def set_time_interval(self, param_time_begin, param_time_end):

        time_begin = param_time(param_time_begin, False)
        time_end = param_time(param_time_end, True)

        if not self.fix_date_begin:
            if time_begin is not None and (self.date_begin is None or time_begin.date() < self.date_begin):
                self.date_begin = time_begin.date()
                self.reset()

        if not self.fix_date_end:
            if time_end is not None and (self.date_end is None or time_end.date() > self.date_end):
                self.date_end = time_end.date()
                self.reset()

        return time_begin, time_end

    def __getattr__(self, item):
        return self.get_indicator(item)

    def get_indicator(self, indicator_name):

        indicator_proxy = self.indicators.get(indicator_name)
        if indicator_proxy is None:
            indicator_proxy = IndicatorProxy(indicator_name, self)
            self.indicators[indicator_name] = indicator_proxy

        return indicator_proxy

    def get_out_from_cache(self, indicator, args, kwargs):
        key = self.key_from_args(indicator, args, kwargs)
        return self.cache.get(key)

    def put_out_to_cache(self, indicator, args, kwargs, out):
        key = self.key_from_args(indicator, args, kwargs)
        self.cache[key] = out

    def reset(self):
        self.cache = {}

    @staticmethod
    def key_from_args(indicator, args, kwargs):
        return args, tuple(kwargs.items())

    # def check_bar_data(self, bar_data):
    #
    #     if self.config['max_empty_bars_fraction'] is None and self.max_empty_bars_consecutive is None:
    #         return
    #
    #     n_bars = len(bar_data.time)
    #     if n_bars == 0: raise FTIException('Bad bar data')
    #
    #     bx_empty_bars = bar_data.volume == 0
    #     n_empty_bars = bx_empty_bars.sum()
    #
    #     empty_bars_fraction = n_empty_bars / n_bars
    #
    #     ix_change = np.flatnonzero(np.diff(bx_empty_bars) != 0) + 1
    #     intervals = np.hstack((ix_change, n_bars)) - np.hstack((0, ix_change))
    #
    #     empty_bars_cons_length = intervals[0 if bx_empty_bars[0] else 1 :: 2]
    #     empty_bars_consecutive = empty_bars_cons_length.max() if len(empty_bars_cons_length) > 0 else 0
    #
    #     if empty_bars_fraction > self.config['max_empty_bars_fraction'] or empty_bars_consecutive > self.config['max_empty_bars_consecutive']:
    #         raise FTIExceptionTooManyEmptyBars(self.datasource_name,
    #                                            bar_data.symbol,
    #                                            bar_data.timeframe,
    #                                            bar_data.first_bar_time,
    #                                            bar_data.end_bar_time,
    #                                            empty_bars_fraction,
    #                                            empty_bars_consecutive)
    #
    #     return empty_bars_fraction, empty_bars_consecutive

    def get_bar_data(self, symbol, timeframe, date_begin, date_end):

        bar_data = self.source_data.get_bar_data(symbol, timeframe, date_begin, date_end)

        self.check_bar_data(bar_data, symbol, date_begin, date_end)

        if self.config['restore_empty_bars']:
            bar_data.restore_bar_data()
        return bar_data

    def check_bar_data(self, bar_data, symbol, date_begin, date_end):

        if self.config['endpoints_required']:
            if len(bar_data) == 0:
                raise FTISourceDataNotFound(symbol, date_begin)
            if bar_data.close[0] == 0:
                raise FTISourceDataNotFound(symbol, date_begin)
            if bar_data.close[-1] == 0:
                raise FTISourceDataNotFound(symbol, date_end)

        max_empty_bars_fraction, max_empty_bars_consecutive = self.config['max_empty_bars_fraction'], self.config['max_empty_bars_consecutive']
        if max_empty_bars_fraction is not None or max_empty_bars_consecutive is not None:

            empty_bars_count, empty_bars_fraction, empty_bars_consecutive = bar_data.get_skips()
            bar_data.data |= {
                'empty_bars_count': empty_bars_count,
                'empty_bars_fraction': empty_bars_fraction,
                'empty_bars_consecutive': empty_bars_consecutive
            }
            if (empty_bars_fraction is not None and empty_bars_fraction > self.config['max_empty_bars_fraction'])\
                    or (empty_bars_consecutive is not None and empty_bars_consecutive > max_empty_bars_consecutive):
                raise FTIExceptionTooManyEmptyBars(self.datasource_name,
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
            raise FTIExceptionIndicatorNotFound(indicator_name)

    def __call__(self, *args, time_begin=None, time_end=None, **kwargs):

        use_date_begin, use_date_end = self.indicators.set_time_interval(time_begin, time_end)

        if use_date_begin is not None and use_date_end is not None and use_date_begin > use_date_end:
            raise ValueError('End date less then begin date')

        out = self.indicators.get_out_from_cache(self.indicator_name, args, kwargs)

        if out is None:
            out = self.indicator_module.get_indicator_out(self.indicators, *args, **kwargs)
            out.read_only = True
            self.indicators.put_out_to_cache(self.indicator_name, args, kwargs, out)

        if (use_date_begin is not None and use_date_begin < out.time[0]) or\
                (use_date_end is not None and out.timeframe.begin_of_tf(use_date_end) > out.time[-1]):
            raise FTIExceptionOutOfThePeriod()

        return out[use_date_begin: use_date_end + out.timeframe.timedelta() if use_date_end else None]

    def __del__(self):
        self.indicator_module = None
        self.indicators = None
