"""MA(period=, value='close', ma_type='sma')
Moving average of different types: 'sma', 'ema', 'mma', 'ema0', 'mma0'"""
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close', ma_type='sma'):

    ma_type_enum = MA_Type.cast(ma_type)

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    out = ma_calculate(source_values, period, ma_type_enum)

    return IndicatorData({
        'name': 'SMA',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'move_average': out,
        'allowed_nan': True
    })


