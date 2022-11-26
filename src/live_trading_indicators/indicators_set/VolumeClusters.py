"""VolumeClusters(timeframe_low='1m', bars_on_bins=6)
OHLCVM and volume clusters is determined by the lower timeframe."""
import numpy as np
from ..indicator_data import IndicatorData
from ..timeframe import Timeframe
from ..exceptions import *
from ..constants import VOLUME_TYPE
from ..volume_clusters import volume_hist


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, timeframe_low='1m', bars_on_bins=5):

    timeframe_low_enum = Timeframe.cast(timeframe_low)

    if timeframe.value % timeframe_low_enum.value > 0:
        raise LTIExceptionBadParameterValue(f'the lower timeframe is not a multiple of the larger one ({timeframe} / {timeframe_low})')

    timeframe_multiple = int(timeframe.value // timeframe_low_enum.value)
    n_bins = timeframe.value // timeframe_low_enum.value // bars_on_bins

    if n_bins < 2:
        raise LTIExceptionBadParameterValue(f'timeframe {timeframe_low_enum} is too large for {timeframe}.')

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    ohlcv_low = indicators.OHLCV.full_data(symbol, timeframe_low_enum)

    hist_volumes, hist_prices = volume_hist(ohlcv_low.low, ohlcv_low.high, ohlcv_low.close, ohlcv_low.volume, n_bins, timeframe_multiple)

    ix_max_volumes = hist_volumes.argmax(1)
    mv_price = (hist_prices[ix_max_volumes] + hist_prices[ix_max_volumes + 1]) / 2

    return IndicatorData({
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