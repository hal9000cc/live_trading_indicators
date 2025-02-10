"""OHLCV()
Quotes: open, high, low, close, volume."""
import numpy as np

from ..constants import PRICE_TYPE, VOLUME_TYPE, TIME_UNITS_IN_ONE_DAY
from ..indicator_data import OHLCV_data
from ..timeframe import Timeframe
from ..exceptions import LTIExceptionTooLittleData


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, **kwargs):

    if timeframe.value <= TIME_UNITS_IN_ONE_DAY:
        return indicators.get_bar_data(symbol, timeframe, out_for_grow)

    ohlcv_days = indicators.OHLCV.full_data(symbol, Timeframe.t1d)
    return build_large_timeframe_from_days(indicators, ohlcv_days, timeframe)


def build_large_timeframe_from_days(indicators, ohlcv_days, timeframe):

    time_days = ohlcv_days.time
    time_begin = timeframe.begin_of_tf(time_days[0])
    if time_begin < time_days[0]: time_begin += timeframe.value

    for i_start, time in enumerate(time_days):
        if time >= time_begin:
            break
    else:
        raise LTIExceptionTooLittleData(f' timeframe {timeframe}, date start {time_days[0]}, date end {ohlcv_days.time[-1]}')

    time_end = timeframe.begin_of_tf(time_days[-1] + TIME_UNITS_IN_ONE_DAY) - TIME_UNITS_IN_ONE_DAY
    #if time_end > time_days[-1]: time_end -= timeframe.value

    for i_end in range(len(time_days) - 1, -1, -1):
        if time_days[i_end] <= time_end:
            break
    else:
        i_end = i_start

    if i_start >= i_end:
        raise LTIExceptionTooLittleData(f' timeframe {timeframe}, date start {time_days[0]}, date end {ohlcv_days.time[-1]}')

    i_end += 1
    time_delta = (time_days[i_start: i_end] - time_begin).astype(np.int64)
    ix_bars = time_delta // timeframe.value
    n_bars = ix_bars[-1] + 1

    time = time_begin + np.arange(n_bars) * timeframe.value
    ix_start_bars = np.where(np.isin(time_days, time))[0]

    open = ohlcv_days.open[ix_start_bars]

    close = ohlcv_days.close[np.hstack([ix_start_bars[1:] - 1, -1])]

    high = np.zeros(len(close), dtype=PRICE_TYPE)
    np.maximum.at(high, ix_bars, ohlcv_days.high[i_start: i_end])

    low = np.full(len(close), ohlcv_days.low.max())
    np.minimum.at(low, ix_bars, ohlcv_days.low[i_start: i_end])

    volume = np.zeros(len(close), dtype=VOLUME_TYPE)
    np.add.at(volume, ix_bars, ohlcv_days.volume[i_start: i_end])

    return OHLCV_data({
        'symbol': ohlcv_days.symbol,
        'timeframe': timeframe,
        'source': ohlcv_days.source,
        'time': time,
        'open': open,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
