import pytest
import numpy as np
from src import live_trading_indicators as lti
from src.live_trading_indicators.constants import TIME_TYPE_UNIT


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-01-01', '2022-01-10')
])
def test_1d_load(clear_data, test_source, test_symbol, time_begin, time_end):
    timeframe = '1d'

    indicators = lti.Indicators('binance', time_begin, time_end, **clear_data)

    ohlcv = indicators.OHLCV(test_symbol, timeframe)

    assert len(ohlcv) == np.datetime64(time_end, 'D') - np.datetime64(time_begin, 'D') + 1


def test_hole_load(clear_data, test_source, test_symbol, a_timeframe):

    indicators = lti.Indicators('binance', **clear_data)
    ohlcv0102 = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-01', '2022-07-02')
    ohlcv06 = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-06', '2022-07-06')

    indicators = lti.Indicators('binance', **clear_data)
    ohlcv = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-01', '2022-07-06')

    assert ohlcv[: np.datetime64('2022-07-03', TIME_TYPE_UNIT)] == ohlcv0102
    assert ohlcv[np.datetime64('2022-07-06', TIME_TYPE_UNIT): ] == ohlcv06