import numpy as np
import datetime as dt
from abc import ABC, abstractmethod

price_type = float


class IndicatorData:

    def __len__(self):
        pass

    def __getitem__(self, item):
        pass


class Indicator(ABC):

    def __init__(self, indicators):
        self.indicators = indicators

    @classmethod
    def indicator_name(cls):
        return cls.__name__

    @abstractmethod
    def recalculate(self, *args, **kwargs):
        pass

    def __del__(self):
        self.indicators = None


class IndicatorException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'{self.__class__.__name__}: {self.message}'
        else:
            return self.__class__.__name__


class IndicatorProxy:

    def __init__(self, indicator, indicators, *args, **kwargs):
        self.indicator = indicator(indicators, *args, **kwargs)
        self.indicators = indicators

    def __call__(self, *args, __full_data__=False, **kwargs):

        out = self.indicators.get_out_from_cache(self.indicator, args, kwargs)

        if out is None:
            out = self.indicator.recalculate(self.indicators, *args, **kwargs)
            self.indicators.put_out_to_cache(self.indicator, args, kwargs, out)

        if __full_data__:
            return out

        assert self.indicators.point <= len(out)
        return out[: self.indicators.i_point]

        assert self.indicators.point <= out.shape[1]
        return out[:, : self.indicators.i_point]

    def __del__(self):
        self.indicator = None
        self.indicators = None

class Indicators:

    @staticmethod
    def key_from_args(indicator, args, kwargs):
        return args, tuple(kwargs.items())

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.indicators = {}
        self.i_point = 0
        self.reset()

    def add_indicator(self, indicator, indicator_name=None, **kwargs):

        if indicator_name is None:
            indicator_name = indicator.indicator_name()

        indicator_proxy = IndicatorProxy(indicator, self, **kwargs)
        self.indicators[indicator_name] = indicator_proxy

        return indicator_proxy.indicator

    def get(self, item):

        indicator_proxy = self.indicators.get(item)
        if indicator_proxy is None:
            raise IndicatorException(f'Indicator not exist: {item}')

        return indicator_proxy

    def __getattr__(self, item):
        return self.get(item)

    def put_out_to_cache(self, indicator, args, kwargs, out):
        key = self.key_from_args(indicator, args, kwargs)
        self.cache[key] = out

    def get_out_from_cache(self, indicator, args, kwargs):
        key = self.key_from_args(indicator, args, kwargs)
        return self.cache.get(key)

    def reset(self):
        self.cache = {}

    def point_get(self):
        return self.i_point

    def point_set(self, point):
        if point == self.i_point:
            return

        self.i_point = point
        #self.reset()

    point = property(point_get, point_set)
