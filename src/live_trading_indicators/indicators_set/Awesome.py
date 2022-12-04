"""Awesome(period_fast=5, period_slow=34, ma_type_fast='smw', ma_type_slow='sma', normalized=False)
Awesome oscillator."""
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow,
                      period_fast=5, period_slow=34, ma_type_fast='sma', ma_type_slow='sma', normalized=False):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    median_price = (ohlcv.high + ohlcv.low) / 2
    ma_fast = ma_calculate(median_price, period_fast, MA_Type.cast(ma_type_fast))
    ma_slow = ma_calculate(median_price, period_slow, MA_Type.cast(ma_type_slow))
    awesome = ma_fast - ma_slow

    if normalized:
        awesome = awesome / median_price

    return IndicatorData({
        'name': 'awesome',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'awesome': awesome,
        'allowed_nan': True
    })

