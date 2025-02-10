import pytest
import src.live_trading_indicators as lti
from src.live_trading_indicators.move_average import ma_calculate, MA_Type
from common_test import *

@pytest.mark.parametrize("time_begin, time_end, period_short", [
    ('2022-07-01', '2022-07-22', 1),
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_vosc(config_default, test_source, time_begin, time_end, period_short, test_symbol):

    timeframe = '5m'
    period_long = 100

    indicators = lti.Indicators(test_source)
    ohlcv = indicators.OHLCV(test_symbol, timeframe, time_begin, time_end)
    vosc = indicators.VolumeOsc(test_symbol, timeframe, time_begin, time_end, period_short=period_short, period_long=period_long)

    vshort = ma_calculate(ohlcv.volume, period_short, MA_Type.ema)
    vlong = ma_calculate(ohlcv.volume, period_long, MA_Type.ema)

    assert compare_with_nan(vosc.osc, (vshort - vlong) / vlong * 100)
