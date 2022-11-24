"""CCI(period=)
Commodity channel index."""
import numpy as np
from numba import njit
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


@njit(cache=True)
def calc_mad(typical_price, sma_typical_price, period):

    values_len = len(sma_typical_price)

    mad = np.empty(values_len)
    mad[:period - 1] = 0
    for i in range(period, values_len + 1):
        mad[i - 1] = np.abs(typical_price[i - period: i] - sma_typical_price[i - 1]).sum() / period

    return mad


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    typical_price = (ohlcv.high + ohlcv.low + ohlcv.close) / 3
    sma_typical_price = ma_calculate(typical_price, period, MA_Type.sma)
    mad = calc_mad(typical_price, sma_typical_price, period)
    cci = (typical_price - sma_typical_price) / mad / 0.015
    cci[mad == 0] = 0

    return IndicatorData({
        'name': 'CCI',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'cci': cci,
        'allowed_nan': True
    })

