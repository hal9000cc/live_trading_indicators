import numpy as np
from ..indicator_data import IndicatorData
from ..constants import PRICE_TYPE
from ..calculator import ema_calculate


def K_calculate(high, low, period):

    U = np.hstack((np.zeros(1, dtype=PRICE_TYPE) + 1e-10, np.diff(source_values)))
    D = -U.copy()

    U[U < 0] = 0
    D[D < 0] = 0

    U = ema_calculate(U, 1.0 / (period + 1))
    D = ema_calculate(D, 1.0 / (period + 1))

    return U / (U + D) * 100


def get_indicator_out(indicators, symbol, timeframe, period_K, period_D, slowing, ma_method='sma'):

    ohlcv = indicators.get_bar_data(symbol, timeframe)
    assert len(ohlcv) > 0

    high = ohlcv.high
    low = ohlcv.low



    return IndicatorData({
        'name': 'RSI',
        'timeframe': timeframe,
        'time': ohlcv.time,
        'value': out
    })

