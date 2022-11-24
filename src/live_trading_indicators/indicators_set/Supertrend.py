"""Supertrend(period=10, multipler=3, ma_type='mma')
Supertrend indicator."""
import numpy as np
from numba import njit
from ..indicator_data import IndicatorData


@njit(cache=True)
def calc_supertrend(close, high, low, atr, multiplier, period):

    start_calculation = period - 1
    data_length = len(close)

    super_trend = np.empty(data_length)
    super_trand_mid = np.empty(data_length)
    super_trend[: start_calculation] = np.nan
    super_trand_mid[: start_calculation] = np.nan

    mid = (high[start_calculation] + low[start_calculation]) / 2.0
    upper_band = mid + (multiplier * atr[start_calculation])
    lower_band = mid - (multiplier * atr[start_calculation])
    trend_up = close[start_calculation] >= mid

    for i in range(start_calculation, len(close)):

        mid = (high[i] + low[i]) / 2.0
        super_trand_mid[i] = mid
        base_upper = mid + (multiplier * atr[i])
        base_lower = mid - (multiplier * atr[i])

        if base_upper < upper_band or close[i - 1] > upper_band:
            upper_band = base_upper

        if base_lower > lower_band or close[i - 1] < lower_band:
            lower_band = base_lower

        if close[i] <= (lower_band if trend_up else upper_band):
            super_trend[i] = upper_band
            trend_up = False
        else:
            super_trend[i] = lower_band
            trend_up = True

    return super_trend, super_trand_mid


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=10, multipler=3, ma_type='mma'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    atr = indicators.ATR.full_data(symbol, timeframe, smooth=period, ma_type=ma_type)

    supertrend, supertrend_mid = calc_supertrend(ohlcv.close, ohlcv.high, ohlcv.low, atr.atr, multipler, period)

    return IndicatorData({
        'name': 'Supertrend',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'supertrend': supertrend,
        'sumpertrend_mid': supertrend_mid,
        'allowed_nan': True
    })

