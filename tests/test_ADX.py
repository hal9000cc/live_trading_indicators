import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-05', 2),
    ('2022-07-01', '2022-07-05', 14)
])
def test_adx(config_default, test_source, a_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    adx = indicators.ADX(a_symbol, timeframe, period=period, smooth=period)

    vadx_ref = si.get_adx(ohlcv2quote(ohlcv), period)

    ref_value_adx = stocks2numpy(vadx_ref, 'adx')
    # ref_value_pdi = stocks2numpy(vadx_ref, 'pdi')
    # ref_value_mdi = stocks2numpy(vadx_ref, 'mdi')
    # ref_value_adxr = stocks2numpy(vadx_ref, 'adxr')

    #assert compare_with_nan(adx.p_di, ref_value_pdi)
    #assert compare_with_nan(adx.m_di, ref_value_mdi)
    assert compare_with_nan(adx.adx, ref_value_adx)
    #assert compare_with_nan(adx.adxr, ref_value_adxr)
