import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period, multiplier, period_atr', [
    ('2022-07-01', '2022-07-10', 2, 1, 2),
    ('2022-07-01', '2022-07-10', 5, 2, 5),
    ('2022-07-01', '2022-07-10', 10, 3, 7)
])
def test_keltner(config_default, test_source, test_symbol, time_begin, time_end, period, multiplier, period_atr):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    keltner = indicators.Keltner(test_symbol, timeframe, period=period, multiplier=multiplier, period_atr=period_atr)

    keltner_ref = si.get_keltner(ohlcv2quote(ohlcv), period, multiplier, period_atr)

    ref_value_mid = stocks2numpy(keltner_ref, 'center_line')
    ref_value_up = stocks2numpy(keltner_ref, 'upper_band')
    ref_value_down = stocks2numpy(keltner_ref, 'lower_band')
    ref_value_width = stocks2numpy(keltner_ref, 'width')

    assert compare_with_nan(keltner.mid_line, ref_value_mid)
    assert compare_with_nan(keltner.up_line, ref_value_up)
    assert compare_with_nan(keltner.down_line, ref_value_down)
    assert compare_with_nan(keltner.width, ref_value_width)

