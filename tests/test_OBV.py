import pytest
from common_test import *
import live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-10'),
    pytest.param((dt.datetime.utcnow() - dt.timedelta(days=2)).date(), None, marks=pytest.mark.live)  # live
])
def test_obv(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    obv = indicators.OBV(test_symbol, timeframe)

    ref_values = get_ref_values('get_obv', ohlcv, 'obv')
    obv = obv[:len(ohlcv)]

    assert compare_with_nan(obv.OBV, ref_values.obv)

