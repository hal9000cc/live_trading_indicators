import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, sma_period', [
    ('2022-07-01', '2022-07-05', 2),
    ('2022-07-01', '2022-07-05', 14)
])
def test_vwap1(config_default, test_source, a_symbol, time_begin, time_end, sma_period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    vwap = indicators.VWAP(a_symbol, timeframe, time_begin, time_end)

    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    vwap_ref = si.get_vwap(ohlcv2quote(ohlcv))

    ref_value_vwap = stocks2numpy(vwap_ref, 'vwap')

    assert compare_with_nan(vwap.vwap, ref_value_vwap, 1e-6)


@pytest.mark.parametrize('time_begin, time_end, sma_period', [
    ('2022-07-10', '2022-07-15', 2),
    ('2022-07-10', '2022-07-15', 14)
])
def test_vwap2(config_default, test_source, a_symbol, time_begin, time_end, sma_period):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, '2022-07-01', '2022-07-31')
    vwap = indicators.VWAP(a_symbol, timeframe, time_begin, time_end)

    ohlcv = indicators.OHLCV(a_symbol, timeframe, time_begin, time_end)
    vwap_ref = si.get_vwap(ohlcv2quote(ohlcv))

    ref_value_vwap = stocks2numpy(vwap_ref, 'vwap')

    assert compare_with_nan(vwap.vwap, ref_value_vwap, 1e-6)

