"""ATR(smooth=14, ma_type='mma')
Average true range."""
import numpy as np
from ..constants import PRICE_TYPE
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, smooth=14, ma_type='mma'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    range_current = ohlcv.high - ohlcv.low
    range_prev_high = np.hstack((np.zeros(1, dtype=PRICE_TYPE), np.abs(ohlcv.close[: -1] - ohlcv.high[1:])))
    range_prev_low = np.hstack((np.zeros(1, dtype=PRICE_TYPE), np.abs(ohlcv.close[: -1] - ohlcv.low[1:])))
    tr = np.vstack((range_current, range_prev_low, range_prev_high)).max(0)
    atr = ma_calculate(tr, smooth, MA_Type.cast(ma_type))

    atrp = atr / ohlcv.close * 100

    return IndicatorData({
        'name': 'ATR',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'tr': tr,
        'atr': atr,
        'atrp': atrp,
        'allowed_nan': True
    })
