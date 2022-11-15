import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_ema(config_default, test_source, test_symbol, time_begin, time_end, period, a_timeframe):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, a_timeframe)
    ema = indicators.EMA(test_symbol, a_timeframe, period=period)

    source_values = ohlcv.close
    values_ema = ema.ema

    alpha = 2.0 / (period + 1)
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
def test_ema_si(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '1m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    ema = indicators.EMA(test_symbol, timeframe, period=period)

    stoch_ref = si.get_ema(ohlcv2quote(ohlcv), period)
    ref_value_ema = stocks2numpy(stoch_ref, 'ema')
    assert (ema.ema[period * 10:] - ref_value_ema[period * 10:] < 1e-4).all()
