"""TEMA(period=, value='close')
Triple exponential moving average."""
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    ema1 = ma_calculate(source_values, period, MA_Type.ema)
    ema2 = ma_calculate(ema1, period, MA_Type.ema0)
    ema3 = ma_calculate(ema2, period, MA_Type.ema0)

    tema = (ema1 * 3) - (ema2 * 3) + ema3

    return IndicatorData({
        'name': 'TEMA',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'tema': tema,
        'allowed_nan': True
    })


