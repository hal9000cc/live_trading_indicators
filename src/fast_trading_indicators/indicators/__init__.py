import importlib
import numpy as np
import datetime as dt
from ..common import *
from .. import datasources


class IndicatorProxy:

    def __init__(self, indicator_name, indicators):
        self.indicator_name = indicator_name
        self.indicator_module = importlib.import_module(f'.{indicator_name}', __package__)
        self.indicators = indicators

    def __call__(self, *args, date_begin=None, date_end=None, **kwargs):

        use_date_begin, use_date_end = self.indicators.set_date_interval(date_begin, date_end)

        if use_date_begin is not None and use_date_end is not None and use_date_begin > use_date_end:
            raise ValueError('The begin date less then the end date')

        out = self.indicators.get_out_from_cache(self.indicator_name, args, kwargs)

        if out is None:
            out = self.indicator_module.get_indicator_out(self.indicators, *args, **kwargs)
            out.read_only = True
            self.indicators.put_out_to_cache(self.indicator_name, args, kwargs, out)

        return out[use_date_begin: use_date_end + dt.timedelta(days=1) if use_date_end else None]

    def __del__(self):
        self.indicator_module = None
        self.indicators = None


class Indicators:

    def __init__(self, datasource,
                 date_begin=None,
                 date_end=None,
                 max_empty_bars_fraction=0.01,  # it's 1%
                 max_empty_bars_consecutive=2,
                 restore_empty_bars=True):  # open=high=low=close = last price

        self.indicators = {}
        self.max_empty_bars_fraction = max_empty_bars_fraction
        self.max_empty_bars_consecutive = max_empty_bars_consecutive
        self.restore_empty_bars = restore_empty_bars

        datasource_type = type(datasource)
        if datasource_type == str:
            datasource_module = importlib.import_module(f'..datasources.{datasource}', __package__)
        elif datasource_type.__name__ == 'module':
            datasource_module = datasource
        else:
            raise TypeError('Bad type of datasource')

        self.datasource_name = datasource_module.datasource_name()
        datasource_module.init()
        self.timeframe_data_cash = datasources.TimeframeData(datasource_module)

        self.date_begin = None
        self.date_end = None

        self.reset()

        self.set_date_interval(date_begin, date_end)

    def set_date_interval(self, inp_date_begin, inp_date_end):

        date_begin = date_from_arg(inp_date_begin)
        date_end = date_from_arg(inp_date_end)

        if date_begin is not None:
            if self.date_begin is None or date_begin < self.date_begin:
                self.date_begin = date_begin
                self.reset()

        if date_end is not None:
            if self.date_end is None or date_end > self.date_end:
                self.date_end = date_end
                self.reset()

        return date_begin, date_end

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

    def check_bar_data(self, bar_data):

        if self.max_empty_bars_fraction is None and self.max_empty_bars_consecutive is None:
            return

        n_bars = len(bar_data.time)
        if n_bars == 0: raise FTIException('Bad bar data')

        bx_empty_bars = bar_data.volume == 0
        n_empty_bars = bx_empty_bars.sum()

        empty_bars_fraction = n_empty_bars / n_bars

        ix_change = np.flatnonzero(np.diff(bx_empty_bars) != 0) + 1
        intervals = np.hstack((ix_change, n_bars)) - np.hstack((0, ix_change))

        empty_bars_cons_length = intervals[0 if bx_empty_bars[0] else 1 :: 2]
        empty_bars_consecutive = empty_bars_cons_length.max() if len(empty_bars_cons_length) > 0 else 0

        if empty_bars_fraction > self.max_empty_bars_fraction or empty_bars_consecutive > self.max_empty_bars_consecutive:
            raise FTIExceptionTooManyEmptyBars(self.datasource_name,
                                               bar_data.symbol,
                                               bar_data.timeframe,
                                               bar_data.first_bar_time,
                                               bar_data.end_bar_time,
                                               empty_bars_fraction,
                                               empty_bars_consecutive)

        return empty_bars_fraction, empty_bars_consecutive

    @staticmethod
    def restore_bar_data(bar_data):

        n_bars = len(bar_data.time)
        bx_empty_bars = bar_data.volume == 0
        ix_change = np.hstack((
            np.zeros(1, dtype=int),
            np.flatnonzero(np.diff(bx_empty_bars)) + 1,
            np.array(n_bars)
        ))

        for i, point in enumerate(ix_change[:-1]):

            if bar_data.volume[point] > 0: continue

            if point == 0:
                price = bar_data.open[ix_change[i + 1]]
            else:
                price = bar_data.close[point - 1]

            point_end = ix_change[i + 1]
            bar_data.open[point : point_end] = price
            bar_data.high[point : point_end] = price
            bar_data.low[point : point_end] = price
            bar_data.close[point : point_end] = price

    def get_bar_data(self, symbol, timeframe, date_begin, date_end):

        bar_data = self.timeframe_data_cash.get_timeframe_data(symbol, timeframe, date_begin, date_end)

        self.check_bar_data(bar_data)

        if self.restore_empty_bars:
            self.restore_bar_data(bar_data)

        return bar_data

