import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period, period_d, smooth', [
    ('2022-07-01', '2022-07-10', 1, 5, 3),
    ('2022-07-01', '2022-07-22', 1, 5, 1),
    ('2022-07-01', '2022-07-22', 1, 1, 1),
    ('2022-07-01', '2022-07-10', 2, 5, 3),
    ('2022-07-01', '2022-07-31', 22, 5, 3),
    ('2022-07-01', '2022-07-22', 22, 5, 3)
])
def test_stohastic(config_default, test_source, test_symbol, time_begin, time_end, period, period_d, smooth, a_big_timeframe):

    test_symbol = 'um/ethusdt'

    indicators = lti.Indicators(test_source)
    ohlcv = indicators.OHLCV(test_symbol, a_big_timeframe, time_begin, time_end)
    stochastic = indicators.Stochastic(test_symbol, a_big_timeframe, time_begin, time_end, period=period, period_d=period_d, smooth=smooth)

    stoch_ref = si.get_stoch(ohlcv2quote(ohlcv), period, period_d, smooth)
    value_d = stocks2numpy(stoch_ref, 'd')
    value_k = stocks2numpy(stoch_ref, 'k')
    oscillator = stocks2numpy(stoch_ref, 'oscillator')

    if smooth < 2:
        assert (stochastic.oscillator - oscillator < 1e-10).all()
    assert (stochastic.value_k[period + smooth - 2:] - value_k[period + smooth - 2:] < 1e-10).all()
    assert (stochastic.value_d[period + period_d + smooth - 3:] - value_d[period + period_d + smooth - 3:] < 1e-10).all()
