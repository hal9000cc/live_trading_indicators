# live_trading_indicators
# MACD(symbol, timeframe, period_short=?, period_long=?, period_signal=?, value='close')

from ..indicator_data import IndicatorData
from ..calculator import ema_calculate, ma_calculate


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period_short, period_long, period_signal,
                      relative_price=False, value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    ema_short = ema_calculate(source_values, 1.0 / (period_short + 1))
    ema_long = ema_calculate(source_values, 1.0 / (period_long + 1))

    macd = ema_short - ema_long
    if relative_price: macd /= source_values / 1000.0

    signal = ma_calculate(macd, period_signal)

    macd_hist = macd - signal

    return IndicatorData({
        'name': 'MACD',
        'timeframe': timeframe,
        'time': ohlcv.time,
        'macd': macd,
        'macd_signal': signal,
        'macd_hist': macd_hist
    })

