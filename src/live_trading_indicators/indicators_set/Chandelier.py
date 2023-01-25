"""Chandelier(period=22, multiplier=3, use_close=False)
Chandelier Exit.
Parameters:
    period - period used for ATR and for finding extremes
    multiplier - multiplier for ATR
    use_close - if true, close is used to calculate the values, otherwise high and low is used"""
import numpy as np
from numba import njit
from ..indicator_data import IndicatorData


@njit(cache=True)
def calc_chandelier(high, low, atr, period, multiplier):

    n_bars = len(high)
    exit_short = np.empty(n_bars, dtype=float)
    exit_long = np.empty(n_bars, dtype=float)

    exit_long[: period - 1] = np.nan
    exit_short[: period - 1] = np.nan
    for i in range(period, n_bars + 1):
        exit_long[i - 1] = high[i - period: i].max() - atr[i - 1] * multiplier
        exit_short[i - 1] = low[i - period: i].min() + atr[i - 1] * multiplier

    return exit_short, exit_long


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=22, multiplier=3, use_close=False):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    atr = indicators.ATR.full_data(symbol, timeframe, smooth=period)

    if use_close:
        high = ohlcv.close
        low = high
    else:
        high = ohlcv.high
        low = ohlcv.low

    exit_short, exit_long = calc_chandelier(high, low, atr.atr, period, multiplier)

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period': period, 'multiplier': multiplier, 'use_close': use_close},
        'name': 'Chandelier',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'exit_short': exit_short,
        'exit_long': exit_long,
        'charts': ('exit_short, exit_long',),
        'allowed_nan': True
    })
