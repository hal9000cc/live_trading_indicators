"""OBV()"""
import numpy as np
from ..constants import PRICE_TYPE
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    signs = np.hstack((0, np.sign(ohlcv.close[1:] - ohlcv.close[:-1])))
    sign_volume = ohlcv.volume * signs
    obv = np.cumsum(sign_volume)

    return IndicatorData({
        'name': 'OBV',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'OBV': obv
    })

