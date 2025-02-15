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
    rsi = indicators.RSI(test_symbol, timeframe, time_begin, time_end, period=period)

    ref_values = get_ref_values('get_rsi', ohlcv, 'rsi', period)

    assert compare_with_nan(rsi.rsi, ref_values.rsi)


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 1),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22),
    ((dt.datetime.utcnow() - dt.timedelta(days=2)).date(), None, 12)  # live
])
def test_rsi1(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    rsi = indicators.RSI(test_symbol, timeframe, period=period)

    ref_values = get_ref_values('get_rsi', ohlcv, 'rsi', period)

    assert compare_with_nan(rsi.rsi, ref_values.rsi)
