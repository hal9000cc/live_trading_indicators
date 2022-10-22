import numpy as np
from ..indicator_data import IndicatorData
from ..calculator import ema_calculate, ma_calculate


def get_indicator_out(indicators, symbol, timeframe, period_ema_short, period_ema_long, period_sma_signal,
                                                                            relative_price=False, value='close'):

    ohlcv = indicators.get_bar_data(symbol, timeframe, indicators.date_begin, indicators.date_end)
    source_values = ohlcv.data[value]

    ema_short = ema_calculate(source_values, 1.0 / (period_ema_short + 1))
    ema_long = ema_calculate(source_values, 1.0 / (period_ema_long + 1))

    macd = ema_short - ema_long
    if relative_price: macd /= source_values / 1000.0

    signal = ma_calculate(macd, period_sma_signal)

    macd_hist = macd - signal

    return IndicatorData({
        'name': 'MACD',
        'timeframe': timeframe,
        'time': ohlcv.time,
        'macd': macd,
        'signal': signal,
        'hist': macd_hist
    })
