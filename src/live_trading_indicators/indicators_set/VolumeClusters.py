"""VolumeClusters(timeframe_low='1m', bars_on_bins=6)
OHLCVM and volume clusters is determined by the lower timeframe."""
import numpy as np
from ..indicator_data import IndicatorData
from ..timeframe import Timeframe
from ..exceptions import *
from ..constants import VOLUME_TYPE
from ..volume_clusters import volume_hist, calendar_volume_hist


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, timeframe_low='1m', bars_on_bins=5):

    timeframe_low_enum = Timeframe.cast(timeframe_low)

    if timeframe_low_enum.is_calendar:
        raise LTIExceptionBadParameterValue('Calendar timeframe_low is not supported for VolumeClusters')

    if timeframe.is_calendar:
        return get_calendar_indicator_out(indicators, symbol, timeframe, timeframe_low, timeframe_low_enum, bars_on_bins)

    if timeframe.value % timeframe_low_enum.value > 0:
        raise LTIExceptionBadParameterValue(f'the lower timeframe is not a multiple of the larger one ({timeframe!s} / {timeframe_low!s})')

    timeframe_multiple = int(timeframe.value // timeframe_low_enum.value)
    n_bins = timeframe.value // timeframe_low_enum.value // bars_on_bins

    if n_bins < 2:
        raise LTIExceptionBadParameterValue(f'timeframe {timeframe_low_enum} is too large for {timeframe!s}.')

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    ohlcv_low = indicators.OHLCV.full_data(symbol, timeframe_low_enum)

    hist_volumes, hist_prices = volume_hist(ohlcv_low.low, ohlcv_low.high, ohlcv_low.close, ohlcv_low.volume, n_bins, timeframe_multiple)

    ix_max_volumes = hist_volumes.argmax(1)
    mv_price = (hist_prices[ix_max_volumes] + hist_prices[ix_max_volumes + 1]) / 2

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'timeframe_low': timeframe_low, 'bars_on_bins': bars_on_bins},
        'name': 'VolumeClusters',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'open': ohlcv.open,
        'high': ohlcv.high,
        'low': ohlcv.low,
        'close': ohlcv.close,
        'volume': ohlcv.volume,
        'mv_price': mv_price,
        'clusters_price': hist_prices,
        'clusters_volume': hist_volumes
    })


def get_calendar_indicator_out(indicators, symbol, timeframe, timeframe_low, timeframe_low_enum, bars_on_bins):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    ohlcv_low = indicators.OHLCV.full_data(symbol, timeframe_low_enum)

    ix_ohlcv, hist_volumes, hist_prices = calendar_volume_hist(ohlcv, ohlcv_low, timeframe, timeframe_low_enum, bars_on_bins)

    ix_max_volumes = hist_volumes.argmax(1)
    mv_price = (hist_prices[np.arange(len(ix_max_volumes)), ix_max_volumes]
                + hist_prices[np.arange(len(ix_max_volumes)), ix_max_volumes + 1]) / 2

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'timeframe_low': timeframe_low, 'bars_on_bins': bars_on_bins},
        'name': 'VolumeClusters',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time[ix_ohlcv],
        'open': ohlcv.open[ix_ohlcv],
        'high': ohlcv.high[ix_ohlcv],
        'low': ohlcv.low[ix_ohlcv],
        'close': ohlcv.close[ix_ohlcv],
        'volume': ohlcv.volume[ix_ohlcv],
        'mv_price': mv_price,
        'clusters_price': hist_prices,
        'clusters_volume': hist_volumes
    })