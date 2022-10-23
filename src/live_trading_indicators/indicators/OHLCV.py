from ..timeframe import *


def get_indicator_out(indicators, symbol, timeframe, **kwargs):

    return indicators.get_bar_data(symbol, Timeframe.cast(timeframe), kwargs['time_begin'], kwargs['time_end'])

