# live_trading_indicators
# RSI(symbol, timeframe, period=?, value='close')

import numpy as np
from ..indicator_data import IndicatorData
from ..constants import PRICE_TYPE
from ..calculator import ema_calculate


def rsi_calculate(source_values, period):

    U = np.hstack((np.zeros(1, dtype=PRICE_TYPE) + 1e-10, np.diff(source_values)))
    D = -U.copy()

    U[U < 0] = 0
    D[D < 0] = 0

    U = ema_calculate(U, 1.0 / (period + 1))
    D = ema_calculate(D, 1.0 / (period + 1))

    return U / (U + D) * 100


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    if len(source_values) == 0:
        out = np.zeros(0, dtype=PRICE_TYPE)
    else:
        out = rsi_calculate(source_values, period)

    return IndicatorData({
        'name': 'RSI',
        'timeframe': timeframe,
        'time': ohlcv.time,
        f'rsi_{value}': out
    })

