"""MFI(period=14)
Money flow index."""
import numpy as np
from ..indicator_data import IndicatorData


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=14):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    n_bars = len(ohlcv)

    typical_price = (ohlcv.high + ohlcv.low + ohlcv.close) / 3
    mf = typical_price * ohlcv.volume
    mfz = np.sign(np.diff(typical_price, prepend=typical_price[0]))

    bx_p = mfz > 0
    mf_p = np.zeros(n_bars, dtype=float)
    mf_p[bx_p] = mf[bx_p]

    bx_m = mfz < 0
    mf_m = np.zeros(n_bars, dtype=float)
    mf_m[bx_m] = mf[bx_m]

    weights = np.ones(period, dtype=float)
    mf_sum_p = np.convolve(mf_p, weights)[: n_bars]
    mf_sum_m = np.convolve(mf_m, weights)[: n_bars]

    mfi = 100.0 * mf_sum_p / (mf_sum_p + mf_sum_m)
    mfi[: period] = np.nan

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period': period},
        'name': 'MFI',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'mfi': mfi,
        'charts': (None, 'mfi, level20:level=20, level80:level=80, ymax:ymax=100, ymin:ymin=0'),
        'allowed_nan': True
    })
