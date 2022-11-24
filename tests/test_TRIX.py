import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 1),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-10', 22),
    ('2022-07-01', '2022-07-10', 14)
])
def test_trix(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    trix = indicators.TRIX(test_symbol, timeframe, period=period)

    trix_ref = si.get_trix(ohlcv2quote(ohlcv), period)

    ref_value_trix = stocks2numpy(trix_ref, 'trix')

    assert compare_with_nan(trix.trix, ref_value_trix)
