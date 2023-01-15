"""WilliamsR(period=14)
Williams %R oscillator."""
import numpy as np
from numba import njit
from ..indicator_data import IndicatorData
from ..exceptions import *


@njit
def calc_williams(high, low, close, period):

    n_bars = len(high)

    williams_r = np.empty(n_bars, dtype=float)

    williams_r[: period - 1] = np.nan
    for t in range(period - 1, n_bars):
        high_max = high[t - period + 1: t + 1].max()
        low_min = low[t - period + 1: t + 1].min()
        williams_r[t] = 0 if high_max == low_min else (close[t] - high_max) / (high_max - low_min) * 100

    return williams_r


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=14):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    data_len = len(ohlcv)
    if data_len < period:
        raise LTIExceptionTooLittleData(f'data length {data_len} < {period}')

    williams_r = calc_williams(ohlcv.high, ohlcv.low, ohlcv.close, period)

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period': period},
        'name': 'WilliamsR',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'williams_r': williams_r,
        'charts': (None, 'williams_r, level20:level=-20, level80:level=-80, ymax:ymax=0, ymin:ymin=-100'),
        'allowed_nan': True
    })


