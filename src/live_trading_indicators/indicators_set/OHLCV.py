from ..timeframe import *


def get_indicator_out(indicators, symbols, timeframe, **kwargs):

    return indicators.get_bar_data(symbols, timeframe)

