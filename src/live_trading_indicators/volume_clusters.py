import numpy as np
from numba import njit
from .constants import VOLUME_TYPE, PRICE_TYPE


@njit(cache=True)
def histogram(values, bins, weights):

    v_min = values.min()
    v_max = values.max()
    step = v_max - v_min
    #levels = np.array([v_min + i * step for i in range(bins)])
    levels = np.empty(bins + 1, dtype=values.dtype)
    hist = np.empty(bins, dtype=weights.dtype)

    for i_level in range(bins - 1):
        level_down = v_min + step * i_level
        level_up = level_down + step
        levels[i_level] = level_down
        hist[i_level] = weights[(values >= level_down) & (values < level_up)].sum()

    level_down = v_min + step * (bins - 1)
    levels[bins - 1] = level_down
    hist[bins - 1] = weights[values >= level_down].sum()

    levels[bins] = v_max
    return hist, levels


@njit(cache=True)
def volume_hist(high, low, close, volume, n_bins, timeframe_multiple):

    len_work_timeframe = len(high) // timeframe_multiple

    vol_div_3 = volume / 3

    hist = np.empty((len_work_timeframe, n_bins), dtype=VOLUME_TYPE)
    hist_prices = np.empty((len_work_timeframe, n_bins + 1), dtype=PRICE_TYPE)

    for i in range(len_work_timeframe):
        i_lt_begin = i * timeframe_multiple
        i_lt_end = i_lt_begin + timeframe_multiple
        bar_prices = np.hstack((high[i_lt_begin: i_lt_end], low[i_lt_begin: i_lt_end], close[i_lt_begin: i_lt_end]))
        bar_volumes = np.hstack((vol_div_3[i_lt_begin: i_lt_end], vol_div_3[i_lt_begin: i_lt_end], vol_div_3[i_lt_begin: i_lt_end]))
        hist[i, :], hist_prices[i, :] = histogram(bar_prices, bins=n_bins, weights=bar_volumes)

    return hist, hist_prices

