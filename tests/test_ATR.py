import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, smooth', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 14),
    ((dt.datetime.utcnow() - dt.timedelta(days=1)).date(), None, 14)  # live
])
def test_atr(config_default, test_source, test_symbol, time_begin, time_end, smooth):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    atr = indicators.ATR(test_symbol, timeframe, smooth=smooth)

    ref_values = get_ref_values('get_atr', ohlcv, 'atr, tr, atrp', smooth)

    assert compare_with_nan(atr.tr[1:], ref_values.tr[1:])
    assert compare_with_nan(atr.atr[300:], ref_values.atr[300:])
    assert compare_with_nan(atr.atrp[300:], ref_values.atrp[300:])
