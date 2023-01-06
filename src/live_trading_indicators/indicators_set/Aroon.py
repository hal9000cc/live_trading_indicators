"""Aroon(period=14)
Aroon oscillator."""
import numpy as np
from numba import njit
from ..indicator_data import IndicatorData


@njit(cache=True)
def calc_aroon(high, low, period):

    up = np.empty(len(high), dtype=float)
    down = np.empty(len(high), dtype=float)
    oscillator = np.empty(len(high), dtype=float)

    up[: period] = np.nan
    down[: period] = np.nan
    oscillator[: period] = np.nan

    for i in range(period, len(high)):
        i_max = period - high[i - period: i + 1].argmax()
        i_min = period - low[i - period: i + 1].argmin()
        up[i] = (period - i_max) / period * 100
        down[i] = (period - i_min) / period * 100
        oscillator[i] = up[i] - down[i]

    return up, down, oscillator


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=14):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    up, down, oscillator = calc_aroon(ohlcv.high, ohlcv.low, period)

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period': period},
        'name': 'Aroon',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'up': up,
        'down': down,
        'oscillator': oscillator,
        'charts': (None, 'up, down', 'oscillator'),
        'allowed_nan': True
    })


