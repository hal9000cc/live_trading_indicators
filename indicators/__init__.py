import os.path
import numpy as np
import datetime as dt
import importlib
from abc import ABC, abstractmethod
from common import *

import datasources
from datasources import TimeframeData


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

    def __init__(self, indicator_name, indicators, *args, **kwargs):
        self.indicator_name = indicator_name
        self.indicator_module = importlib.import_module(f'indicators.{indicator_name}')
        self.indicators = indicators

    def __call__(self, *args, __full_data__=False, **kwargs):

        out = self.indicators.get_out_from_cache(self.indicator_name, args, kwargs)

        if out is None:
            out = self.indicator_module.make_out(self.indicators, *args, **kwargs)
            self.indicators.put_out_to_cache(self.indicator_name, args, kwargs, out)

        if __full_data__:
            return out

        return out[:, : self.indicators.i_point]

    def __del__(self):
        self.indicator_module = None
        self.indicators = None


class Indicators:

    def __init__(self, datasource_name, **kwargs):

        datasource = importlib.import_module(datasource_name)
        datasource.init()
        self.timeframe_data_cash = datasources.TimeframeData(datasource, **kwargs)

        self.indicators = {}
        self.reset()

    def __getattr__(self, item):
        return self.get(item)

    def get(self, indicator_name):

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

