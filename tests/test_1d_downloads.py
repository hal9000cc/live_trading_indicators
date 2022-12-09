import pytest
import numpy as np
from src import live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-01-01', '2022-01-10')
])
def test_1d_load(clear_data, test_source, test_symbol, time_begin, time_end):
    timeframe = '1d'

    indicators = lti.Indicators('binance', time_begin, time_end, **clear_data)

    ohlcv = indicators.OHLCV(test_symbol, timeframe)

    assert len(ohlcv) == np.datetime64(time_end, 'D') - np.datetime64(time_begin, 'D') + 1
