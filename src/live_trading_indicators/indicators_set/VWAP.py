"""VWAP()
Volume-weighted average price."""
import numpy as np
from ..indicator_data import IndicatorData

no_cached = True


def get_indicator_out(indicators, symbol, timeframe, time_begin, time_end):

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

    typical_price = (ohlcv.close + ohlcv.high + ohlcv.low) / 3
    volume_sum = np.cumsum(ohlcv.volume)
    vwap = np.cumsum(typical_price * ohlcv.volume) / volume_sum

    return IndicatorData({
        'name': 'VWAP',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'vwap': vwap,
        'allowed_nan': True
    })
