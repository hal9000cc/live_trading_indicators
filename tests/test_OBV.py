import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-10')
])
def test_obv(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '1m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    obv = indicators.OBV(test_symbol, timeframe)

    stoch_ref_obv = si.get_obv(ohlcv2quote(ohlcv))

    ref_value_obv = stocks2numpy(stoch_ref_obv, 'obv')

    assert (obv.OBV - ref_value_obv < 1e-12).all()

