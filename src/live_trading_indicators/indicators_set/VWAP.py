"""VWAP()
Volume-weighted average price."""
import numpy as np
from ..indicator_data import IndicatorData

no_cached = True

OUTPUT_SERIES = (
    {'name': 'vwap', 'type': 'price', 'range': None},
)


def get_indicator_out(indicators, symbol, timeframe, time_begin, time_end):

    ohlcv = indicators.OHLCV.data(symbol, timeframe, time_begin, time_end)

    typical_price = (ohlcv.close + ohlcv.high + ohlcv.low) / 3
    volume_sum = np.cumsum(ohlcv.volume)
    vwap = np.cumsum(typical_price * ohlcv.volume) / volume_sum

    return IndicatorData({
        'indicators': indicators,
        'parameters': {},
        'name': 'VWAP',
        'output_series': OUTPUT_SERIES,
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'vwap': vwap,
        'allowed_nan': True
    })
