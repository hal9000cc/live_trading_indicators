import importlib
from ..common import *
from .. import datasources


class IndicatorProxy:

    def __init__(self, indicator_name, indicators):
        self.indicator_name = indicator_name
        self.indicator_module = importlib.import_module(f'.{indicator_name}', __package__)
        self.indicators = indicators

    def __call__(self, *args, inp_date_begin=None, inp_date_end=None, **kwargs):

        date_begin, date_end = self.indicators.set_date_interval(inp_date_begin, inp_date_end)

        out = self.indicators.get_out_from_cache(self.indicator_name, args, kwargs)

        if out is None:
            out = self.indicator_module.get_indicator_out(self.indicators, *args, **kwargs)
            self.indicators.put_out_to_cache(self.indicator_name, args, kwargs, out)

        return out[date_begin : date_end]

    def __del__(self):
        self.indicator_module = None
        self.indicators = None


class Indicators:

    def __init__(self, datasource, date_begin=None, date_end=None, common_data_path=None):

        self.indicators = {}

        datasource_type = type(datasource)
        if datasource_type == str:
            datasource_module = importlib.import_module(f'..datasources.{datasource}', __package__)
        elif datasource_type.__name__ == 'module':
            datasource_module = datasource
        else:
            raise TypeError('Bad type of datasource')

        datasource_module.init(common_data_path)
        self.timeframe_data_cash = datasources.TimeframeData(datasource_module, common_data_path=common_data_path)

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

        if date_end is not None:
            if self.date_end is None or date_end > self.date_end:
                self.date_end = date_end

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

    def reset(self):
        self.cache = {}

    @staticmethod
    def key_from_args(indicator, args, kwargs):
        return args, tuple(kwargs.items())

