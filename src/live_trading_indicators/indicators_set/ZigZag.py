"""ZigZag_pivots(delta=0.02, type='high_low', redrawable=False)
Zig-zag indicator (pivots).
Return pivots prices and pivots types.
Parameters:
    delta - fraction of the price change at which the corner is formed (float)
    type - price values used for corners (can be 'high_low', 'close', 'open', 'high', 'low')
    redrawable - if True, incomplete pivots will be formed at the end"""

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


@njit(cache=True)
def add_last_point(pivot_types, pivots, high, low, delta):

    n_bars = len(high)

    i_last_point = 0
    for i in range(1, n_bars + 1):
        if pivot_types[n_bars - i] != 0:
            i_last_point = n_bars - i
            break

    last_pivot_type = pivot_types[i_last_point]
    if last_pivot_type == 0:
        last_pivot_type = high.max() - low[0] > high[0] - low.min()
        pivot_types[i_last_point] = last_pivot_type

    if last_pivot_type > 0:
        i_min = i_last_point + low[i_last_point:].argmin()
        pivot_min = low[i_min]
        if (high[i_last_point] - pivot_min) / high[i_last_point] > delta:
            pivot_types[i_min] = -1
            if i_min < n_bars - 1:
                pivot_types[n_bars - 1] = 1
    else:
        i_max = i_last_point + high[i_last_point:].argmax()
        pivot_max = high[i_max]
        if (pivot_max - low[i_last_point]) / low[i_last_point] > delta:
            pivot_types[i_max] = 1
            if i_max < n_bars - 1:
                pivot_types[n_bars - 1] = -1

    ix_new_points_max = i_last_point + np.flatnonzero(pivot_types[i_last_point:] > 0)
    ix_new_points_min = i_last_point + np.flatnonzero(pivot_types[i_last_point:] < 0)
    pivots[ix_new_points_max] = high[ix_new_points_max]
    pivots[ix_new_points_min] = low[ix_new_points_min]


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, delta=0.02, type='high_low', redrawable=False):

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
        if (pivots[i_valid] - low[: i_valid].min()) / pivots[i_valid] < delta:
            i_valid += 1
    else:
        if (high[: i_valid].max() - pivots[i_valid]) / pivots[i_valid] < delta:
            i_valid += 1

    pivots[: i_valid] = np.nan
    pivot_types[: i_valid] = 0

    if redrawable:
        add_last_point(pivot_types, pivots, high, low, delta)

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


