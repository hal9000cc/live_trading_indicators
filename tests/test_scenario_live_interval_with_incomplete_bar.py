import pytest
import numpy as np
import datetime as dt
import time
from src import live_trading_indicators as lti
from src.live_trading_indicators.constants import TIME_TYPE, TIME_TYPE_UNIT


@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m, lti.Timeframe.t1h])
def test_fix_live_with_incomplete_1(config_default, test_source, a_symbol, timeframe):

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 10:
        time.sleep(remain_time_sec)

    time_begin = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT) - timeframe.value
    indicators = lti.Indicators(test_source, time_begin, with_incomplete_bar=True)

    while True:
        ohlcv = indicators.OHLCV(a_symbol, timeframe)
        if len(ohlcv.time) == 2: break
        assert len(ohlcv.time) == 1

    n_bars = len(ohlcv.time)
    assert n_bars == 2

    time.sleep(5)
    ohlcv1 = indicators.OHLCV(a_symbol, timeframe)
    assert ohlcv.volume[-1] <= ohlcv1.volume[-1]


def test_fix_live_with_incomplete_2(config_default, test_source, a_symbol):

    timeframe = lti.Timeframe.t1m

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 10:
        time.sleep(remain_time_sec)

    now = dt.datetime.utcnow()
    time_begin = np.datetime64(now, 'D')
    indicators = lti.Indicators(test_source, time_begin, with_incomplete_bar=True)

    time.sleep(3)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)

    n_bars = len(ohlcv.time)
    assert n_bars == (np.datetime64(now, 'm') - np.datetime64(time_begin, 'm')).astype(np.int64) + 1

    next_time = timeframe.begin_of_tf(now) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)

    if remain_time_sec > 0:
        time.sleep(remain_time_sec)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    assert len(ohlcv.time) == n_bars or len(ohlcv.time) == n_bars + 1

    time.sleep(5)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    assert len(ohlcv.time) == n_bars + 1


def test_fix_live_with_incomplete_3(config_default, test_source, test_symbol, a_timeframe):

    next_time = a_timeframe.begin_of_tf(dt.datetime.utcnow()) + a_timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 30:
        time.sleep(remain_time_sec + 5)

    now = dt.datetime.utcnow()
    time_begin = np.datetime64(now, 'D')
    indicators = lti.Indicators(test_source, time_begin, with_incomplete_bar=True)

    ohlcv = indicators.OHLCV(test_symbol, a_timeframe)

    time.sleep(5)
    ohlcv1 = indicators.OHLCV(test_symbol, a_timeframe)
    assert ohlcv.time[-1] == ohlcv1.time[-1]
    assert ohlcv.volume[-1] != ohlcv1.volume[-1]
