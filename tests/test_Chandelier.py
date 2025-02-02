import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period, multiplier', [
    ('2022-07-01', '2022-07-10', 2, 3),
    ('2022-07-01', '2022-07-10', 20, 2.5),
    ((dt.datetime.utcnow() - dt.timedelta(days=2)).date(), None, 20, 2.5)  # live
])
def test_chandelier(config_default, test_source, test_symbol, time_begin, time_end, period, multiplier):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    chandelier = indicators.Chandelier(test_symbol, timeframe, period=period, multiplier=multiplier)

    ref_values_short = get_ref_values('get_chandelier', ohlcv, 'chandelier_exit', period, multiplier, 'SHORT')
    ref_values_long = get_ref_values('get_chandelier', ohlcv, 'chandelier_exit', period, multiplier, 'LONG')

    assert compare_with_nan(chandelier.exit_short[500:], ref_values_short.chandelier_exit[500:])
    assert compare_with_nan(chandelier.exit_long[500:], ref_values_long.chandelier_exit[500:])


