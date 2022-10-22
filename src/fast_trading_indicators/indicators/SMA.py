import numpy as np
from ..calculator import ma_calculate
from ..indicator_data import IndicatorData


def get_indicator_out(indicators, symbol, timeframe, period, value='close'):

    ohlcv = indicators.get_bar_data(symbol, timeframe, indicators.date_begin, indicators.date_end)
    source_values = ohlcv.data[value]

    data_len = len(source_values)
    if data_len < period:
        raise ValueError(f'Period SMA more then data size ({data_len} < {period})')

    out = ma_calculate(source_values, period)

    return IndicatorData({
        'name': 'SMA',
        'timeframe': timeframe,
        'time': ohlcv.time,
        'value': out
    })

