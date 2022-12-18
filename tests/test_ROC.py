import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 14)
])
def test_roc(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    roc = indicators.ROC(test_symbol, timeframe, period=period)

    ref_values = get_ref_values('get_roc', ohlcv, 'roc, roc_sma', period, 14)

    assert compare_with_nan(roc.roc * 100, ref_values.roc)
    assert compare_with_nan(roc.smooth_roc * 100, ref_values.roc_sma)
