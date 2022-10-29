import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period, ma_type', [
    ('2022-07-01', '2022-07-10', 3, 'sma'),
    ('2022-07-01', '2022-07-10', 5, 'ema'),
    ('2022-07-01', '2022-07-31', 22, 'sma'),
    ('2022-07-01', '2022-07-22', 22, 'ema')
])
def test_ema(config_default, test_source, test_symbol, time_begin, time_end, period, ma_type, a_timeframe):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ma = indicators.MA(test_symbol, a_timeframe, period=period, ma_type=ma_type)
