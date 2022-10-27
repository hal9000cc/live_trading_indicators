import numpy as np
from ..indicator_data import IndicatorData
from ..calculator import ema_calculate


def get_indicator_out(indicators, symbol, timeframe, period, value='close'):

    ohlcv = indicators.get_bar_data(symbol, timeframe, indicators.date_begin, indicators.date_end)
    values = ohlcv.data[value]

    alpha = 1.0 / (period + 1)
    out = ema_calculate(values, alpha)

    return IndicatorData({
        'name': 'EMA',
        'timeframe': timeframe,
        'time': ohlcv.time,
        'value': out
    })

