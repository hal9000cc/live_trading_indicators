import numpy as np
from numba import njit
from .constants import VOLUME_TYPE, PRICE_TYPE
from .exceptions import LTIExceptionBadParameterValue, LTIExceptionTooLittleData


@njit(cache=True)
def histogram(values, bins, weights):

    v_min = values.min()
    v_max = values.max()

    step = (v_max - v_min) / bins
    levels = np.empty(bins + 1, dtype=values.dtype)
    hist = np.empty(bins, dtype=weights.dtype)

    level_down = v_min
    for i_level in range(bins):

        level_up = v_min + (i_level + 1) * step
        levels[i_level] = level_down

        if i_level == bins - 1:
            hist[i_level] = weights[values >= level_down].sum()
        else:
            hist[i_level] = weights[(values >= level_down) & (values < level_up)].sum()

        level_down = level_up

    levels[bins] = level_down
    return hist, levels


@njit(cache=True)
def volume_hist(low, high, close, volume, n_bins, timeframe_multiple):

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


@njit(cache=True)
def volume_hist_by_index_ranges(low, high, close, volume, n_bins, ix_begin, ix_end):

    len_work_timeframe = len(ix_begin)

    vol_div_3 = volume / 3

    hist = np.empty((len_work_timeframe, n_bins), dtype=VOLUME_TYPE)
    hist_prices = np.empty((len_work_timeframe, n_bins + 1), dtype=PRICE_TYPE)

    for i in range(len_work_timeframe):
        i_lt_begin = ix_begin[i]
        i_lt_end = ix_end[i]
        bar_prices = np.hstack((high[i_lt_begin: i_lt_end], low[i_lt_begin: i_lt_end], close[i_lt_begin: i_lt_end]))
        bar_volumes = np.hstack((vol_div_3[i_lt_begin: i_lt_end], vol_div_3[i_lt_begin: i_lt_end], vol_div_3[i_lt_begin: i_lt_end]))
        hist[i, :], hist_prices[i, :] = histogram(bar_prices, bins=n_bins, weights=bar_volumes)

    return hist, hist_prices


def calendar_volume_hist(ohlcv, ohlcv_low, timeframe, timeframe_low, bars_on_bins):

    ix_ohlcv = []
    ix_begin = []
    ix_end = []
    low_bars_counts = []

    for i_bar, time_begin in enumerate(ohlcv.time):
        time_end = timeframe.next_bar_time(time_begin)
        i_begin = int(np.searchsorted(ohlcv_low.time, time_begin, side='left'))
        i_end = int(np.searchsorted(ohlcv_low.time, time_end, side='left'))
        bars_count = int((time_end - time_begin).astype(np.int64) // timeframe_low.value)

        is_complete = \
            i_begin < len(ohlcv_low.time) and \
            i_end > i_begin and \
            i_end - i_begin == bars_count and \
            ohlcv_low.time[i_begin] == time_begin and \
            ohlcv_low.time[i_end - 1] + timeframe_low.value == time_end

        if not is_complete:
            if len(ix_ohlcv) == 0:
                continue
            break

        ix_ohlcv.append(i_bar)
        ix_begin.append(i_begin)
        ix_end.append(i_end)
        low_bars_counts.append(bars_count)

    if len(ix_ohlcv) == 0:
        raise LTIExceptionTooLittleData(f'timeframe_low {timeframe_low}, timeframe {timeframe!s}')

    n_bins = min(low_bars_counts) // bars_on_bins
    if n_bins < 2:
        raise LTIExceptionBadParameterValue(f'timeframe {timeframe_low} is too large for {timeframe!s}.')

    hist_volumes, hist_prices = volume_hist_by_index_ranges(
        ohlcv_low.low,
        ohlcv_low.high,
        ohlcv_low.close,
        ohlcv_low.volume,
        n_bins,
        np.array(ix_begin, dtype=np.int64),
        np.array(ix_end, dtype=np.int64)
    )

    return np.array(ix_ohlcv, dtype=np.int64), hist_volumes, hist_prices

