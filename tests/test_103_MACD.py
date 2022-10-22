import pytest
import src.fast_trading_indicators as fti


@pytest.mark.parametrize('time_begin, time_end, period_ema_short, period_ema_long, period_sma_signal', [
    ('2022-07-01', '2022-07-10', 21, 8, 3),
    ('2022-07-01', '2022-07-10', 8, 21, 1)
])
def test_rsi(config_default, default_source, default_symbol, time_begin, time_end,
                        period_ema_short, period_ema_long, period_sma_signal, a_timeframe):

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, a_timeframe, time_begin=time_begin, time_end=time_end)
    macd = indicators.MACD(default_symbol, a_timeframe, period_ema_short, period_ema_long, period_sma_signal, time_begin=time_begin, time_end=time_end)

    # need check values!