import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 14)
])
def test_vwma(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    vwma = indicators.VWMA(test_symbol, timeframe, period=period)

    vwma_ref = si.get_vwma(ohlcv2quote(ohlcv), period)

    ref_value_vwma = stocks2numpy(vwma_ref, 'vwma')

    assert compare_with_nan(vwma.vwma, ref_value_vwma, 1e-9)
