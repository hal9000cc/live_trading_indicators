import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-05', 14),
    ('2022-07-01', '2022-07-05', 2)
])
def test_adx(config_default, test_source, a_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    adx = indicators.ADX(a_symbol, timeframe, period=period, smooth=period)

    ref_values = get_ref_values('get_adx', ohlcv, 'adx, pdi, mdi', period)

    assert compare_with_nan(adx.p_di[200:], ref_values.pdi[200:], 1e-5)
    assert compare_with_nan(adx.m_di[200:], ref_values.mdi[200:], 1e-5)
    assert compare_with_nan(adx.adx, ref_values.adx)

