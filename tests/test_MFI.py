import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 20),
    ((dt.datetime.utcnow() - dt.timedelta(days=2)).date(), None, 5)  # live
])
def test_mfi(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    mfi = indicators.MFI(test_symbol, timeframe, period=period)

    ref_values = get_ref_values('get_mfi', ohlcv, 'mfi', period)

    assert compare_with_nan(mfi.mfi, ref_values.mfi)


