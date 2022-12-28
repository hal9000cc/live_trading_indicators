"""OBV()
On Balance Volume."""
import numpy as np
from ..constants import PRICE_TYPE
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type

no_cached = True


def get_indicator_out(indicators, symbol, timeframe, time_begin, time_end):

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

    signs = np.hstack((0, np.sign(ohlcv.close[1:] - ohlcv.close[:-1])))
    sign_volume = ohlcv.volume * signs
    obv = np.cumsum(sign_volume)

    return IndicatorData({
        'indicators': indicators,
        'parameters': {},
        'name': 'OBV',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'OBV': obv,
        'charts': (None, 'OBV')
    })

