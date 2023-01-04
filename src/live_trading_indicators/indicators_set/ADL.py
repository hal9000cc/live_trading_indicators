"""ADL(ma_period=None, ma_type='sma')
Accumulation/distribution line.
Parameters:
    ma_period - moving average period (int) for adl_smooth value, it can be None if adl_smooth is not needed
    ma_type - moving average type for adl_smooth value (can be 'sma', 'ema', 'mma', 'ema0', 'mma0')"""

from ..indicator_data import IndicatorData
from ..move_average import *

no_cached = True


def get_indicator_out(indicators, symbol, timeframe, time_begin, time_end, ma_period=None, ma_type='sma'):

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

    np.seterr(invalid='ignore')
    hl_range = ohlcv.high - ohlcv.low
    clv = ((ohlcv.close - ohlcv.low) - (ohlcv.high - ohlcv.close)) / hl_range
    clv[hl_range == 0] = 0

    adl = np.cumsum(clv * ohlcv.volume)

    result_data = {
        'indicators': indicators,
        'parameters': {'ma_period': ma_period, 'ma_type': ma_type},
        'name': 'ADL',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'adl': adl,
        'charts': (None, 'adl'),
        'allowed_nan': True
    }

    if ma_period is not None:
        result_data.update({'adl_smooth': ma_calculate(adl, ma_period, MA_Type.cast(ma_type))})

    return IndicatorData(result_data)
