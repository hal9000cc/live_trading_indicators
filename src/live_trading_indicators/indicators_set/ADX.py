"""ADX(period=14, smooth=14, ma_type='mma')
Average directional movement index."""
from ..indicator_data import IndicatorData
from ..move_average import *


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=14, smooth=14, ma_type='mma'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    data_len = len(ohlcv)
    if data_len < period:
        raise LTIExceptionTooLittleData(f'data length {data_len} < {period}')

    ma_type_enum = MA_Type.cast(ma_type)

    high = ohlcv.high
    low = ohlcv.low

    p_dm = np.hstack([np.nan, np.diff(high)])
    m_dm = np.hstack([np.nan, -np.diff(low)])

    bx_zero_p_dm = (p_dm <= m_dm) | (p_dm < 0)
    bx_zero_m_dm = (m_dm <= p_dm) | (m_dm < 0)
    p_dm[bx_zero_p_dm] = 0
    m_dm[bx_zero_m_dm] = 0

    atr = indicators.ATR.full_data(symbol, timeframe, smooth=period)

    p_di = 100 * ma_calculate(p_dm, period, ma_type_enum) / atr.atr
    m_di = 100 * ma_calculate(m_dm, period, ma_type_enum) / atr.atr

    dxi = 100 * abs(p_di - m_di) / (p_di + m_di)
    dxi[p_di + m_di == 0] = 0

    adx = ma_calculate(dxi, period, ma_type_enum)

    return IndicatorData({
        'name': 'ADX',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'adx': adx,
        'p_di': p_di,
        'm_di': m_di,
        'allowed_nan': True
    })


