"""ZigZag_pivots(delta=0.01, type='high_low')
Zig-zag indicator (pivots).
Return pivots prices and pivots types.
Parameters:
    delta - fraction of the price change at which the corner is formed (float)
    type - price values used for corners (can be 'high_low', 'close', 'open', 'high', 'low')"""

import numpy as np
from numba import njit
from ..indicator_data import IndicatorData
from ..exceptions import *
from ..constants import PRICE_TYPE


@njit(cache=True)
def find_up_corner(i_point, high, low, delta):

    i_up_corner = i_point
    up_corner = high[i_point]
    for i in range(i_point + 1, len(high)):
        if high[i] >= up_corner:
            up_corner = high[i]
            i_up_corner = i
            continue
        elif (up_corner - low[i]) / up_corner >= delta:
            return i_up_corner, i

    return i_up_corner, len(high)


@njit(cache=True)
def find_down_corner(i_point, high, low, delta):

    i_down_corner = i_point
    down_corner = low[i_point]
    for i in range(i_point + 1, len(high)):
        if low[i] <= down_corner:
            down_corner = low[i]
            i_down_corner = i
            continue
        elif (high[i] - down_corner) / down_corner >= delta:
            return i_down_corner, i

    return i_down_corner, len(high)


@njit(cache=True)
def calc_pivots(direction, high, low, delta, pivots, pivot_types, checking):

    n_bars = len(high)

    i_point = 0
    while i_point < n_bars:

        if direction > 0:

            i_up_corner, i_point = find_up_corner(i_point, high, low, delta)
            if i_point >= n_bars: break

            if checking and pivot_types[i_up_corner] == 1:
                return i_up_corner

            pivot_types[i_up_corner] = 1
            up_corner = high[i_up_corner]
            pivots[i_up_corner] = up_corner
            direction = -1

        else:

            i_down_corner, i_point = find_down_corner(i_point, high, low, delta)
            if i_point >= n_bars: break

            if checking and pivot_types[i_down_corner] == -1:
                return i_down_corner

            pivot_types[i_down_corner] = -1
            down_corner = low[i_down_corner]
            pivots[i_down_corner] = down_corner
            direction = 1


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, delta=0.01, type='high_low'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    if type == 'high_low':
        high, low = ohlcv.high, ohlcv.low
    elif type in {'open', 'high', 'low', 'close'}:
        high, low = ohlcv.data[type]
    else:
        raise LTIExceptionBadParameterValue(f'type = {type}')

    n_bars = len(ohlcv)
    pivots = np.ndarray(n_bars, dtype=PRICE_TYPE)
    pivot_types = np.zeros(n_bars, dtype=np.int8)
    pivots[:] = np.nan

    calc_pivots(-1, high, low, delta, pivots, pivot_types, False)
    i_valid = calc_pivots(1, high, low, delta, pivots, pivot_types, True)

    if pivot_types[i_valid] > 0:
        if (pivots[i_valid] - ohlcv.low[: i_valid].min()) / pivots[i_valid] < delta:
            i_valid += 1
    else:
        if (ohlcv.high[: i_valid].max() - pivots[i_valid]) / pivots[i_valid] < delta:
            i_valid += 1

    pivots[: i_valid] = np.nan
    pivot_types[: i_valid] = 0

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'delta': delta},
        'name': 'ZigZag',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'pivots': pivots,
        'pivot_types': pivot_types,
        'charts': ('pivots:pivots',),
        'allowed_nan': True
    })


