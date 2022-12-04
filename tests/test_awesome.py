import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period_fast, period_slow', [
    ('2022-07-01', '2022-07-10', 2, 5),
    ('2022-07-01', '2022-07-10', 3, 7),
    ('2022-07-01', '2022-07-10', 15, 20),
    ('2022-07-01', '2022-07-10', 12, 20)
])
def test_awesome(config_default, test_source, test_symbol, time_begin, time_end, period_fast, period_slow):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    awesome = indicators.awesome(test_symbol, timeframe, period_fast=period_fast, period_slow=period_slow)

    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    awesome_ref = si.get_awesome(ohlcv2quote(ohlcv), period_fast, period_slow)

    ref_value_oscillator = stocks2numpy(awesome_ref, 'oscillator')

    assert compare_with_nan(awesome.awesome, ref_value_oscillator)


