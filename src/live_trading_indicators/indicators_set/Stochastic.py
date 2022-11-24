"""Stochastic(period=, period_d=, smooth=3, ma_type='sma')
Stochastic oscillator."""
import numpy as np
from numba import njit
from ..move_average import ma_calculate, MA_Type
from ..indicator_data import IndicatorData


@njit(cache=True)
def calc_k(high, low, close, period):

    value_k = np.empty(len(close), dtype=float)
    value_k[: period - 1] = np.nan

    for i in range(period - 1, len(close)):
        v_high = high[i - period + 1: i + 1].max()
        v_low = low[i - period + 1: i + 1].min()
        value_k[i] = 0 if v_high == v_low else (close[i] - v_low) / (v_high - v_low) * 100

    return value_k


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, period_d, smooth=3, ma_type='sma'):

    ma_type_enum = MA_Type.cast(ma_type)

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    oscillator = calc_k(ohlcv.high, ohlcv.low, ohlcv.close, period)
    value_k = ma_calculate(oscillator, smooth, ma_type_enum)
    value_d = ma_calculate(value_k, period_d, ma_type_enum)

    return IndicatorData({
        'name': 'Stochastic',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'value_d': value_d,
        'value_k': value_k,
        'oscillator': oscillator,
        'allowed_nan': True
    })

