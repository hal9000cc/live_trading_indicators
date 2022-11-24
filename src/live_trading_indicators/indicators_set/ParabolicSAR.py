"""ParabolicSAR(start=0.02, maximum=0.2, increment=0.02)
Parabolic SAR."""

import numpy as np
from numba import njit
from ..indicator_data import IndicatorData
from ..exceptions import *
from ..constants import PRICE_TYPE


@njit(cache=True)
def calc_paraboic(highs, lows, start, maximum, increment):

    sars = np.empty(len(highs), dtype=PRICE_TYPE)
    #sars[0] = np.nan
    signals = np.zeros(len(highs), dtype=np.int8)

    is_bullish = True
    acceleration_factor = start
    sar = lows[0]
    extreme = highs[0]

    for i in range(1, len(highs)):

        sar += acceleration_factor * (extreme - sar)

        if is_bullish:

            if i > 1:
                sar = min(sar, lows[i - 1], lows[i - 2])

            if lows[i] < sar:
                is_bullish = False
                signals[i] = -1
                sar = extreme
                acceleration_factor = start
                extreme = lows[i]
            else:
                if highs[i] > extreme:
                    extreme = highs[i]
                    acceleration_factor = min(acceleration_factor + increment, maximum)

        else:

            if i > 1:
                sar = max(sar, highs[i - 1], highs[i - 2])

            if highs[i] > sar:
                is_bullish = True
                signals[i] = 1
                sar = extreme
                acceleration_factor = start
                extreme = highs[i]
            else:
                if lows[i] < extreme:
                    extreme = lows[i]
                    acceleration_factor = min(acceleration_factor + increment, maximum)

        sars[i] = sar

    for i, signal in enumerate(signals):
        sars[i] = np.nan
        signals[i] = 0
        if signal != 0:
            break

    return sars, signals


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, start=0.02, maximum=0.2, increment=0.02):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    data_len = len(ohlcv)
    min_data_len = 3
    if len(ohlcv) < min_data_len:
        raise LTIExceptionTooLittleData(f'data length {data_len} < {min_data_len}')

    parabolic_sar, signals = calc_paraboic(ohlcv.high, ohlcv.low, start, maximum, increment)

    return IndicatorData({
        'name': 'ParabolicSAR',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'sar': parabolic_sar,
        'signal': signals,
        'allowed_nan': True
    })

