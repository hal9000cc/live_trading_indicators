from .SMA import get_indicator_out as sma_get_indicator_out
from .EMA import get_indicator_out as ema_get_indicator_out
from ..move_average import MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close', ma_type='sma'):

    ma_type_enum = MA_Type.cast(ma_type)
    match ma_type_enum:
        case MA_Type.sma:
            return sma_get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value)
        case MA_Type.ema:
            return ema_get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value)

    raise NotImplementedError()

