import numpy as np
from ..indicator_data import IndicatorData


def get_indicator_out(indicators, symbol, timeframe, period, value='close', **kwargs):

    ohlcv = indicators.get_bar_data(symbol, timeframe, indicators.date_begin, indicators.date_end)
    values = ohlcv.data[value]

    data_len = len(values)
    if data_len < period:
        raise ValueError(f'Period SMA more then data size ({data_len} < {period})')

    weights = np.ones(period, dtype=values.dtype) / period

    out = np.convolve(values, weights)[:-period+1]
    begin_multiple = period / np.arange(1, period, dtype=float)
    out[:period - 1] *= begin_multiple

    return IndicatorData({
        'name': 'SMA',
        'timeframe': timeframe,
        'time': ohlcv.time,
        'value': out
    })

