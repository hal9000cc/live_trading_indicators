"""ZigZag(delta=0.02, depth=1, type='high_low', end_points=False)
Zig-zag indicator (pivots).
Return pivots prices and pivots types.
Parameters:
    delta - fraction of the price change at which the corner is formed (float)
    depth - minimum distance pivots H-H and L-L
    type - price values used for corners (can be 'high_low', 'close', 'open', 'high', 'low')
    end_points - if True, incomplete pivots will be formed at the end"""

import numpy as np
from numba import njit
from ..indicator_data import IndicatorData
from ..exceptions import *
from ..constants import PRICE_TYPE

no_cached = True


@njit(cache=True)
def find_up_corner(i_point, high, low, delta, depth):

    n_bars = len(high)
    i_up_corner = i_point
    up_corner = high[i_point]
    i = i_point + 1
    while i < n_bars:
        if high[i] > up_corner:
            while True:
                i_up_corner = i + high[i: min(i + depth, n_bars)].argmax()
                up_corner = high[i_up_corner]
                if i_up_corner == i: break
                i = i_up_corner
        elif (up_corner - low[i]) / up_corner >= delta:
            return i_up_corner, i
        i += 1

    return i_up_corner, len(high)


@njit(cache=True)
def find_down_corner(i_point, high, low, delta, depth):

    n_bars = len(high)
    i_down_corner = i_point
    down_corner = low[i_point]
    i = i_point + 1
    while i < n_bars:
        if low[i] < down_corner:
            while True:
                i_down_corner = i + low[i: min(i + depth, n_bars)].argmin()
                down_corner = low[i_down_corner]
                if i_down_corner == i: break
                i = i_down_corner
        elif (high[i] - down_corner) / down_corner >= delta:
            return i_down_corner, i
        i += 1

    return i_down_corner, len(high)


@njit(cache=True)
def calc_pivots(direction, high, low, delta, pivots, pivot_types, depth, checking):

    n_bars = len(high)

    i_point = 0
    while i_point < n_bars:

        if direction > 0:

            i_up_corner, i_point = find_up_corner(i_point, high, low, delta, depth)
            if i_point >= n_bars: break

            if checking and pivot_types[i_up_corner] == 1:
                return i_up_corner

            pivot_types[i_up_corner] = 1
            up_corner = high[i_up_corner]
            pivots[i_up_corner] = up_corner
            direction = -1

        else:

            i_down_corner, i_point = find_down_corner(i_point, high, low, delta, depth)
            if i_point >= n_bars: break

            if checking and pivot_types[i_down_corner] == -1:
                return i_down_corner

            pivot_types[i_down_corner] = -1
            down_corner = low[i_down_corner]
            pivots[i_down_corner] = down_corner
            direction = 1


@njit(cache=True)
def add_last_point(pivot_types, pivots, high, low, delta, depth):

    n_bars = len(high)

    i_last_point = 0
    for i in range(1, n_bars + 1):
        if pivot_types[n_bars - i] != 0:
            i_last_point = n_bars - i
            break

    last_pivot_type = pivot_types[i_last_point]
    if last_pivot_type == 0:
        return

    if last_pivot_type > 0:
        pivot_types[-1] = -1
        pivots[-1] = low[-1]
    else:
        pivot_types[1] = 1
        pivots[-1] = high[-1]


def get_indicator_out(indicators, symbol, timeframe, time_begin, time_end, delta=0.02, depth=1, type='high_low', end_points=False):

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

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

    calc_pivots(-1, high, low, delta, pivots, pivot_types, depth, False)
    i_valid = calc_pivots(1, high, low, delta, pivots, pivot_types, depth, True)

    if i_valid is not None:
        if pivot_types[i_valid] > 0:
            if (pivots[i_valid] - low[: i_valid].min()) / pivots[i_valid] < delta:
                i_valid += 1
        else:
            if (high[: i_valid].max() - pivots[i_valid]) / pivots[i_valid] < delta:
                i_valid += 1

        pivots[: i_valid] = np.nan
        pivot_types[: i_valid] = 0

    if end_points:
        add_last_point(pivot_types, pivots, high, low, delta, depth)

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'delta': delta, 'depth': depth, 'end_points': end_points},
        'name': 'ZigZag',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'pivots': pivots,
        'pivot_types': pivot_types,
        'charts': ('pivots:pivots',),
        'allowed_nan': True
    })


