import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-10'),
    ((dt.datetime.utcnow() - dt.timedelta(days=2)).date(), None)  # live
])
def test_obv(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    obv = indicators.OBV(test_symbol, timeframe)

    ref_values = get_ref_values('get_obv', ohlcv, 'obv')

    assert compare_with_nan(obv.OBV, ref_values.obv)

