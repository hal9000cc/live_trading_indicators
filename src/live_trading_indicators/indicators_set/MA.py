# live_trading_indicators
# MA(symbol, timeframe, period=?, value='close', ma_type='sma')

from .SMA import get_indicator_out as sma_get_indicator_out
from .EMA import get_indicator_out as ema_get_indicator_out


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close', ma_type='sma'):

    if ma_type == 'sma':
        return sma_get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value)
    elif ma_type == 'ema':
        return ema_get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value)

    raise NotImplementedError()

