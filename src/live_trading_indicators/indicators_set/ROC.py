"""ROC(period=14, ma_period=14, ma_type='sma', value='close')
Rate of Change."""
import numpy as np
from ..constants import PRICE_TYPE
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=14, ma_period=14, ma_type='sma', value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    roc = (source_values[period:] - source_values[: -period]) / source_values[: -period]
    smooth_roc = ma_calculate(roc, ma_period, MA_Type.cast(ma_type))

    begin = np.array([np.nan] * period, dtype=PRICE_TYPE)

    return IndicatorData({
        'name': 'ROC',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'roc': np.hstack((begin, roc)),
        'smooth_roc': np.hstack((begin, smooth_roc)),
        'allowed_nan': True
    })

