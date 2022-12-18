import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, sma_period', [
    ('2022-07-01', '2022-07-05', 2),
    ('2022-07-01', '2022-07-05', 14)
])
def test_adl1(config_default, test_source, a_symbol, time_begin, time_end, sma_period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end, **config_default)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    adl = indicators.ADL(a_symbol, timeframe, ma_period=sma_period)

    ref_values = get_ref_values('adl', ohlcv, 'adl, adl_sma', sma_period)

    assert compare_with_nan(adl.adl, ref_values.adl, 1e-6)
    assert compare_with_nan(adl.adl_smooth, ref_values.adl_sma, 1e-6)


@pytest.mark.parametrize('time_begin, time_end, sma_period', [
    ('2022-07-10', '2022-07-15', 2),
    ('2022-07-10', '2022-07-15', 14)
])
def test_adl2(config_default, test_source, time_begin, time_end, sma_period):

    a_symbol = 'um/ethusdt'
    timeframe = '1m'

    indicators = lti.Indicators(test_source, '2022-07-01', '2022-07-31')
    ohlcv = indicators.OHLCV(a_symbol, timeframe, time_begin, time_end)
    adl = indicators.ADL(a_symbol, timeframe, time_begin, time_end, ma_period=sma_period)

    ref_values = get_ref_values('adl', ohlcv, 'adl, adl_sma', sma_period)

    assert compare_with_nan(adl.adl, ref_values.adl, 1e-6)
    assert compare_with_nan(adl.adl_smooth, ref_values.adl_sma, 1e-6)
