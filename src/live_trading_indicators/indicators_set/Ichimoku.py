"""Ichimoku(period_short=9, period_mid=26, period_long=52, offset_senkou=26, offset_chikou=26)
Ichimoku indicator."""
from numba import njit
import numpy as np
from ..indicator_data import IndicatorData
from ..constants import PRICE_TYPE


@njit(cache=True)
def calc_av_min_max(high, low, period):

    n_bars = len(high)

    av_min_max = np.empty(n_bars, dtype=PRICE_TYPE)

    av_min_max[: period - 1] = np.nan
    for t in range(period - 1, n_bars):
        av_min_max[t] = (high[t - period + 1: t + 1].max() + low[t - period + 1: t + 1].min()) / 2

    return av_min_max


def offset_ahead(series, period):
    series[period:] = series[: -period]
    series[: period] = np.nan


def get_indicator_out(indicators, symbol, timeframe, out_for_grow,
                      period_short=9, period_mid=26, period_long=52, offset_senkou=26, offset_chikou=26):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    high = ohlcv.high
    low = ohlcv.low

    tenkan = calc_av_min_max(high, low, period_short)
    kijun = calc_av_min_max(high, low, period_mid)

    senkou_a = np.vstack((tenkan, kijun)).sum(0) / 2
    offset_ahead(senkou_a, offset_senkou)

    senkou_b = calc_av_min_max(high, low, period_long)
    offset_ahead(senkou_b, offset_senkou)

    chikou = np.empty(len(high), dtype=PRICE_TYPE)
    chikou[: -offset_chikou] = ohlcv.close[offset_chikou:]
    chikou[-offset_chikou:] = np.nan

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period_short': period_short, 'period_mid': period_mid,
                       'period_long': period_long, 'offset_senkou': offset_senkou, 'offset_chikou': offset_chikou},
        'name': 'Ichimoku',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'tenkan': tenkan,
        'kijun': kijun,
        'senkou_a': senkou_a,
        'senkou_b': senkou_b,
        'chikou': chikou,
        'charts': ('tenkan, kijun, chikou, senkou_a:dashed, senkou_b:dashed, senkou_a:cloud:senkou_b', ),
        'allowed_nan': True
    })

