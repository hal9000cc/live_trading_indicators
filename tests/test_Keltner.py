import pytest
from common_test import *
import src.live_trading_indicators as lti


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

    ref_values = get_ref_values('get_keltner', ohlcv, 'center_line, upper_band, lower_band, width', period, multiplier, period_atr)

    assert compare_with_nan(keltner.mid_line, ref_values.center_line)
    assert compare_with_nan(keltner.up_line, ref_values.upper_band)
    assert compare_with_nan(keltner.down_line, ref_values.lower_band)
    assert compare_with_nan(keltner.width, ref_values.width)

