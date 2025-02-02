import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period_fast, period_slow', [
    ('2022-07-01', '2022-07-10', 2, 5),
    ('2022-07-01', '2022-07-10', 3, 7),
    ('2022-07-01', '2022-07-10', 15, 20),
    ('2022-07-01', '2022-07-10', 12, 20),
    ((dt.datetime.utcnow() - dt.timedelta(days=1)).date(), None, 14, 20)  # live
])
def test_awesome(config_default, test_source, test_symbol, time_begin, time_end, period_fast, period_slow):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    awesome = indicators.Awesome(test_symbol, timeframe, period_fast=period_fast, period_slow=period_slow)

    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    ref_values = get_ref_values('get_awesome', ohlcv, 'oscillator', period_fast, period_slow)

    assert compare_with_nan(awesome.awesome, ref_values.oscillator)


