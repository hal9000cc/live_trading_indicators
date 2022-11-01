import pytest
import numpy as np
import datetime as dt
import time
from src import live_trading_indicators as lti
from src.live_trading_indicators.constants import TIME_TYPE, TIME_TYPE_UNIT


@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m, lti.Timeframe.t1h])
def test_live_1(config_default, test_source, a_symbol, timeframe):

    time_begin = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT) - timeframe.value * 2
    indicators = lti.Indicators(test_source, time_begin)

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(int)
    if remain_time_sec < 10:
        time.sleep(remain_time_sec)

    while True:
        ohlcv = indicators.OHLCV(a_symbol, timeframe)
        if len(ohlcv.time) == 2: break
        assert len(ohlcv.time) == 1

    n_bars = len(ohlcv.time)
    assert n_bars == 2

    time.sleep(5)
    ohlcv1 = indicators.OHLCV(a_symbol, timeframe)
    assert ohlcv == ohlcv1


@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m])
def test_live_2(config_default, test_source, a_symbol, timeframe):

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(int)
    if remain_time_sec < 10:
        time.sleep(remain_time_sec)

    time_begin = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT) - timeframe.value * 2
    indicators = lti.Indicators(test_source, time_begin)

    time.sleep(5)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(int)
    time.sleep(remain_time_sec)

    time.sleep(5)
    ohlcv1 = indicators.OHLCV(a_symbol, timeframe)
    assert ohlcv == ohlcv1[:-1]

