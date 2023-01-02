import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period, period_d, smooth', [
    ('2022-07-01', '2022-07-22', 1, 5, 1),
    ('2022-07-01', '2022-07-10', 1, 5, 3),
    ('2022-07-01', '2022-07-22', 1, 1, 1),
    ('2022-07-01', '2022-07-10', 2, 5, 3),
    ('2022-07-01', '2022-07-31', 22, 5, 3),
    ('2022-07-01', '2022-07-22', 21, 5, 3),
    ('2022-07-01', '2022-07-22', 20, 5, 3),
    ('2022-07-01', '2022-07-22', 19, 5, 3),
    ('2022-07-01', '2022-07-22', 18, 5, 3),
    ('2022-07-01', '2022-07-22', 17, 5, 3),
    ('2022-07-01', '2022-07-22', 16, 5, 3),
    ('2022-07-01', '2022-07-22', 15, 5, 3),
    ('2022-07-01', '2022-07-22', 14, 5, 3),
    ('2022-07-01', '2022-07-22', 13, 5, 3),
    ('2022-07-01', '2022-07-22', 12, 5, 3)
])
def test_stohastic(config_default, test_source, test_symbol, time_begin, time_end, period, period_d, smooth, a_big_timeframe):

    indicators = lti.Indicators(test_source)
    ohlcv = indicators.OHLCV(test_symbol, a_big_timeframe, time_begin, time_end)
    stochastic = indicators.Stochastic(test_symbol, a_big_timeframe, time_begin, time_end, period=period, period_d=period_d, smooth=smooth)

    ref_values = get_ref_values('get_stoch', ohlcv, 'd, k, oscillator', period, period_d, smooth)

    if smooth == 1:
        assert compare_with_nan(stochastic.oscillator, ref_values.oscillator)
    assert compare_with_nan(stochastic.value_k, ref_values.k)
    assert compare_with_nan(stochastic.value_d, ref_values.d)


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-05')
])
def test_stockhastic_plot(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcvm = indicators.Stochastic(test_symbol, timeframe)

    ohlcvm.show()
