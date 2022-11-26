"""OHLCVM(timeframe_low='1m', bars_on_bins=6)
Quotes and the price of the maximum volume: open, high, low, close, volume, mv_price.
The price of the maximum volume is determined by the lower timeframe (default 1m)."""
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

    ix_max_volumes_wdims = np.expand_dims(ix_max_volumes, axis=1)
    mv_price = (np.take_along_axis(hist_prices, ix_max_volumes_wdims, 1)
                + np.take_along_axis(hist_prices, ix_max_volumes_wdims + 1, 1)) / 2

    return IndicatorData({
        'name': 'OHLCVM',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'open': ohlcv.open,
        'high': ohlcv.high,
        'low': ohlcv.low,
        'close': ohlcv.close,
        'volume': ohlcv.volume,
        'mv_price': mv_price
    })