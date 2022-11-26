import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-10')
])
def test_obv(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    obv = indicators.OBV(test_symbol, timeframe)

    obv_ref = si.get_obv(ohlcv2quote(ohlcv))

    ref_value_obv = stocks2numpy(obv_ref, 'obv')

    assert compare_with_nan(obv.OBV, ref_value_obv)

