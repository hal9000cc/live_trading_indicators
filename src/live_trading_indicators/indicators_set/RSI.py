import numpy as np
from ..indicator_data import IndicatorData
from ..constants import PRICE_TYPE
from ..move_average import ma_calculate, MA_Type


def rsi_calculate(source_values, period, ma_type):

    U = np.hstack((np.zeros(1, dtype=PRICE_TYPE) + 1e-10, np.diff(source_values)))
    D = -U.copy()

    U[U < 0] = 0
    D[D < 0] = 0

    U_smooth = ma_calculate(U, period, ma_type)
    D_smooth = ma_calculate(D, period, ma_type)

    divider = U_smooth + D_smooth
    res = U_smooth / divider * 100
    res[divider == 0] = 100
    assert not np.isnan(res).any()
    return res


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, ma_type='ema', value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    if len(source_values) == 0:
        out = np.zeros(0, dtype=PRICE_TYPE)
    else:
        out = rsi_calculate(source_values, period, MA_Type.cast(ma_type))

    return IndicatorData({
        'name': 'RSI',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'rsi': out
    })

