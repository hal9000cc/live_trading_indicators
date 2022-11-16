import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 20),
    ('2022-07-01', '2022-07-10', 20)
])
def test_cci(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    cci = indicators.CCI(test_symbol, timeframe, period=period)

    cc_ref = si.get_cci(ohlcv2quote(ohlcv), period)

    ref_value_cci = stocks2numpy(cc_ref, 'cci')

    ref_value_cci[np.isnan(ref_value_cci)] = 0
    assert (cci.cci[period - 1:] - ref_value_cci[period - 1:] < 1e-10).all()


