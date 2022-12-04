import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, sma_period', [
    ('2022-07-01', '2022-07-05', 2),
    ('2022-07-01', '2022-07-05', 14)
])
def test_adl1(config_default, test_source, a_symbol, time_begin, time_end, sma_period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    adl = indicators.ADL(a_symbol, timeframe, ma_period=sma_period)

    adl_ref = si.get_adl(ohlcv2quote(ohlcv), sma_period)

    ref_value_adl = stocks2numpy(adl_ref, 'adl')
    ref_value_adl_sma = stocks2numpy(adl_ref, 'adl_sma')

    assert compare_with_nan(adl.adl, ref_value_adl, 1e-6)
    assert compare_with_nan(adl.adl_smooth, ref_value_adl_sma, 1e-6)


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

    adl_ref = si.get_adl(ohlcv2quote(ohlcv), sma_period)

    ref_value_adl = stocks2numpy(adl_ref, 'adl')
    ref_value_adl_sma = stocks2numpy(adl_ref, 'adl_sma')

    assert compare_with_nan(adl.adl, ref_value_adl, 1e-6)
    assert compare_with_nan(adl.adl_smooth, ref_value_adl_sma, 1e-6)
