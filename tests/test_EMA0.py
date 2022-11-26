import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_ema0(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    ema0 = indicators.MA(test_symbol, timeframe, period=period, ma_type='ema0')

    source_values = ohlcv.close
    values_ema1 = ema0.move_average

    alpha = 2.0 / (period + 1)
    alpha_n = 1.0 - alpha
    ema_value = source_values[0]
    for i, value in enumerate(source_values):
        ema_value = value * alpha + ema_value * alpha_n
        assert values_ema1[i] - ema_value < 1e-12
