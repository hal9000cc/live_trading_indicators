import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 1),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_rsi(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '1m'

    indicators = lti.Indicators(test_source)
    ohlcv = indicators.OHLCV(test_symbol, timeframe, time_begin, time_end)
    rsi = indicators.RSI(test_symbol, timeframe, time_begin, time_end, period=period)

    rsi_ref = si.get_rsi(ohlcv2quote(ohlcv), period)
    rsi_ref_values = stocks2numpy(rsi_ref, 'rsi')

    assert compare_with_nan(rsi_ref_values, rsi.rsi)
