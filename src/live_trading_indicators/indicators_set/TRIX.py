"""TRIX(period=, value='close')
TRIX oscillator."""
import numpy as np

from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    ema1 = ma_calculate(source_values, period, MA_Type.ema)
    ema2 = ma_calculate(ema1, period, MA_Type.ema0)
    ema3 = ma_calculate(ema2, period, MA_Type.ema0)

    trix = np.diff(ema3) / ema3[: -1] * 100

    return IndicatorData({
        'name': 'TRIX',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'trix': np.hstack([np.nan, trix]),
        'allowed_nan': True
    })


