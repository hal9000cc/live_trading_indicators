"""Keltner(period=10, multiplier=1, period_atr=10, ma_type='ema', ma_type_atr='mma')
Keltner channel."""
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow,
                      period=10, multiplier=1, period_atr=10, ma_type='ema', ma_type_atr='mma'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    atr = indicators.ATR.full_data(symbol, timeframe, smooth=period_atr, ma_type=ma_type_atr)

    mid_line = ma_calculate(ohlcv.close, period, MA_Type.cast(ma_type))
    up_line = mid_line + atr.atr * multiplier
    down_line = mid_line - atr.atr * multiplier

    return IndicatorData({
        'name': 'Keltner',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'mid_line': mid_line,
        'up_line': up_line,
        'down_line': down_line,
        'width': (up_line - down_line) / mid_line,
        'allowed_nan': True
    })

