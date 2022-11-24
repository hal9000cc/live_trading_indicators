import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 14)
])
def test_adx(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    roc = indicators.ROC(test_symbol, timeframe, period=period)

    roc_ref = si.get_roc(ohlcv2quote(ohlcv), period, 14)

    ref_value_roc = stocks2numpy(roc_ref, 'roc')
    ref_value_roc_sma = stocks2numpy(roc_ref, 'roc_sma')

    assert compare_with_nan(roc.roc * 100, ref_value_roc)
    assert compare_with_nan(roc.smooth_roc * 100, ref_value_roc_sma)
