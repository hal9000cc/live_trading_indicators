import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-01-01', '2022-07-31'),
    ('2022-01-01', '2022-07-31')
])
def test_ohlcvm(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcvm = indicators.OHLCVM(test_symbol, timeframe)

    pass