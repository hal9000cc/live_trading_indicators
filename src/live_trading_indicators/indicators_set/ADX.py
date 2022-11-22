"""ADX(period=, ma_type='mma')"""
import numpy as np
from ..indicator_data import IndicatorData
from ..exceptions import *
from ..move_average import *


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, ma_type='mma'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    data_len = len(ohlcv)
    if data_len < period:
        raise LTIExceptionTooLittleData(f'data length {data_len} < {period}')

    ma_type_enum = MA_Type.cast(ma_type)

    high = ohlcv.high
    low = ohlcv.low

    plus_m = high[1:] - high[:-1]
    minus_m = low[:-1] - low[1:]

    plus_dm = np.zeros(data_len - 1, dtype=float)
    minus_dm = np.zeros(data_len - 1, dtype=float)

    bx_update_plus_dm = (plus_m > minus_m) & (plus_m > 0)
    plus_dm[bx_update_plus_dm] = plus_m[bx_update_plus_dm]

    bx_update_minus_dm = (minus_m > plus_m) & (minus_m > 0)
    minus_dm[bx_update_minus_dm] = minus_m[bx_update_minus_dm]

    atr = indicators.ATR.full_data(symbol, timeframe, smooth=period, ma_type=ma_type).atr

    plus_di = ma_calculate(plus_dm / atr[1:], period, ma_type_enum)[period - 1:]
    minus_di = ma_calculate(minus_dm / atr[1:], period, ma_type_enum)[period - 1:]

    adx = 100 * ma_calculate((plus_di - minus_di) / (plus_di + minus_di), period, ma_type_enum)
    adx = np.hstack([np.empty(period, dtype=adx.dtype), adx])
    adx[:period] = np.nan

    return IndicatorData({
        'name': 'ADX',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'adx': adx,
        'allowed_nan': True
    })


