import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 1),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_rsi(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source)
    ohlcv = indicators.OHLCV(test_symbol, timeframe, time_begin, time_end)
    williams_r = indicators.WilliamsR(test_symbol, timeframe, time_begin, time_end, period=period)

    ref_values = get_ref_values('get_williams_r', ohlcv, 'williams_r', period)

    assert compare_with_nan(williams_r.williams_r, ref_values.williams_r)
