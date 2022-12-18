import numpy as np
import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_mma(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    ema = indicators.MA(test_symbol, timeframe, period=period, ma_type='mma0')

    source_values = ohlcv.close
    values_ema = ema.move_average

    alpha = 1.0 / period
    alpha_n = 1.0 - alpha
    ema_value = source_values[0]
    for i, value in enumerate(source_values):
        ema_value = value * alpha + ema_value * alpha_n
        assert round(values_ema[i], 8) == round(ema_value, 8)


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 2),
    ('2022-07-01', '2022-07-10', 1),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 8),
    ('2022-07-01', '2022-07-22', 10)
])
def test_ema(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    ima = indicators.MA(test_symbol, timeframe, period=period, ma_type='ema')

    ref_values = get_ref_values('get_ema', ohlcv, 'ema', period)

    assert compare_with_nan(ima.move_average, ref_values.ema)
