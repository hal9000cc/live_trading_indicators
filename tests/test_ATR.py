import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, smooth', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 14)
])
def test_atr(config_default, test_source, test_symbol, time_begin, time_end, smooth):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    atr = indicators.ATR(test_symbol, timeframe, smooth=smooth)

    atr_ref = si.get_atr(ohlcv2quote(ohlcv), smooth)

    ref_value_atr = stocks2numpy(atr_ref, 'atr')
    ref_value_tr = stocks2numpy(atr_ref, 'tr')
    ref_value_atrp = stocks2numpy(atr_ref, 'atrp')

    assert compare_with_nan(atr.tr, ref_value_tr)
    assert compare_with_nan(atr.atr, ref_value_atr)
    assert compare_with_nan(atr.atrp, ref_value_atrp)
