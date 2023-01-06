import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-02', '2022-07-10', 7),
    ('2022-07-03', '2022-07-10', 14)
])
def test_aroon(config_default, test_source, a_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    aroon = indicators.Aroon(a_symbol, timeframe, period=period)

    ref_values = get_ref_values('get_aroon', ohlcv, 'aroon_up, aroon_down, oscillator', period)

    assert compare_with_nan(aroon.up, ref_values.aroon_up)
    assert compare_with_nan(aroon.down, ref_values.aroon_down)
    assert compare_with_nan(aroon.oscillator, ref_values.oscillator)

