"""VWMA(period=, value='close')
Volume Weighted Moving Average."""
import numpy as np
from numba import njit
from ..indicator_data import IndicatorData
from ..exceptions import *


@njit(cache=True)
def vwma_calculate(values, volume, period):

    vwma = np.empty(len(values), dtype=float)
    vwma[: period - 1] = np.nan

    volume_sum = volume[: period].sum()
    vwsum = (values[: period] * volume[: period]).sum()
    vwma[period - 1] = vwsum / volume_sum
    for i in range(period, len(values)):
        vwsum -= values[i - period] * volume[i - period]
        vwsum += values[i] * volume[i]
        volume_sum -= volume[i - period]
        volume_sum += volume[i]
        vwma[i] = vwsum / volume_sum

    return vwma


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    data_len = len(ohlcv)
    if data_len < period:
        raise LTIExceptionTooLittleData(f'data length {data_len} < {period}')

    source_values = ohlcv.data[value]

    vwma = vwma_calculate(source_values, ohlcv.volume, period)

    return IndicatorData({
        'name': 'VWMA',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'vwma': vwma,
        'allowed_nan': True
    })


