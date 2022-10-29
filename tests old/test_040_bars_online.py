import pytest
import datetime as dt
import numpy as np
import src.live_trading_indicators as lti
from src.live_trading_indicators.common import param_time
from src.live_trading_indicators.datasources import binance



@pytest.mark.parametrize('symbol, timeframe, date_begin', [
    ('um/btcusdt', '1h', 20221019),
    ('um/ethusdt', '1h', 20221018)
])
def test_bar_dates(config_default, test_source, symbol, timeframe, date_begin):

    date_end = dt.date.today()
    indicators = lti.Indicators(test_source, date_begin, date_end)
    ohlcv = indicators.OHLCV(symbol, timeframe)

    assert ohlcv.time[0] == lti.Timeframe.cast(timeframe).begin_of_tf(param_time(date_begin, False))
    assert ohlcv.time[-1] == lti.Timeframe.cast(timeframe).begin_of_tf(dt.datetime.utcnow())