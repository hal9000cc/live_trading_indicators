"""EMA(period=, value='close')"""
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    out = ma_calculate(source_values, period, MA_Type.ema)

    return IndicatorData({
        'name': 'EMA',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'ema': out,
        'allowed_nan': True
    })


