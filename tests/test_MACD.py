import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period_ema_short, period_ema_long, period_sma_signal', [
    ('2022-07-01', '2022-07-10', 21, 8, 3),
    ('2022-07-01', '2022-07-10', 8, 21, 1)
])
def test_macd(config_default, test_source, test_symbol, time_begin, time_end,
             period_ema_short, period_ema_long, period_sma_signal, a_timeframe):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    out = indicators.OHLCV(test_symbol, a_timeframe)
    macd = indicators.MACD(test_symbol, a_timeframe, period_short=period_ema_short, period_long=period_ema_long, period_signal=period_sma_signal)

    # need check values!