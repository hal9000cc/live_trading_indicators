"""ADL(ma_period=None, ma_type='sma')
Accumulation/distribution line."""
from ..indicator_data import IndicatorData
from ..move_average import *

no_cached = True


def get_indicator_out(indicators, symbol, timeframe, time_begin, time_end, ma_period=None, ma_type='sma'):

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

    hl_range = ohlcv.high - ohlcv.low
    clv = ((ohlcv.close - ohlcv.low) - (ohlcv.high - ohlcv.close)) / hl_range
    clv[hl_range == 0] = 0

    adl = np.cumsum(clv * ohlcv.volume)

    result_data = {
        'name': 'ADL',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'adl': adl,
        'allowed_nan': True
    }

    if ma_period is not None:
        result_data |= {'adl_smooth': ma_calculate(adl, ma_period, MA_Type.cast(ma_type))}

    return IndicatorData(result_data)
