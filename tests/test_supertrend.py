import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 20),
    ('2022-07-01', '2022-07-10', 20)
])
def test_supertrend(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    supertrend = indicators.Supertrend(test_symbol, timeframe, period=period)
    ref_values = get_ref_values('get_super_trend', ohlcv, 'super_trend', period)

    assert compare_with_nan(supertrend.supertrend, ref_values.super_trend)


