import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_rsi(config_default, test_source, test_symbol, time_begin, time_end, period, a_timeframe):

    indicators = lti.Indicators(test_source)
    out = indicators.OHLCV(test_symbol, a_timeframe, time_begin, time_end)
    rsi = indicators.RSI(test_symbol, a_timeframe, time_begin, time_end, period=period)

    # need check values!