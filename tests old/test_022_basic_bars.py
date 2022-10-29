import pytest
import importlib
import numpy as np
import src.live_trading_indicators as lti
from src.live_trading_indicators.common import param_time
from src.live_trading_indicators.datasources import binance


@pytest.mark.parametrize('symbol, timeframe, date_begin, date_end, time_begin, time_end', [
    ('um/btcusdt', lti.Timeframe.t1h, 20220701, 20220731, '2022-07-02T20:00', '2022-07-02T23:00'),
    ('um/btcusdt', lti.Timeframe.t1h, 20220701, 20220731, '2022-07-02T20:00', '2022-07-04T15:00'),
    ('um/btcusdt', lti.Timeframe.t1h, 20220701, 20220731, 20220702, 20220703)
])
def test_bar_dates(config_default, test_source, symbol, timeframe, date_begin, date_end, time_begin, time_end):

    indicators = lti.Indicators(test_source, date_begin, date_end)
    macd = indicators.MACD(symbol, timeframe, 18, 25, 3, time_begin=time_begin, time_end=time_end)

    use_time_begin, use_time_end = param_time(time_begin, False), param_time(time_end, True)
    use_time_begin, use_time_end = timeframe.begin_of_tf(use_time_begin), timeframe.begin_of_tf(use_time_end)
    assert macd.time[0] == np.datetime64(use_time_begin)
    assert macd.time[-1] == np.datetime64(use_time_end)

    indicators = lti.Indicators(test_source)
    macd = indicators.MACD(symbol, timeframe, 18, 25, 3, time_begin=time_begin, time_end=time_end)

    assert macd.time[0] == np.datetime64(use_time_begin)
    assert macd.time[-1] == np.datetime64(use_time_end)
