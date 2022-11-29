import pytest
import numpy as np
import datetime as dt
import time
from src import live_trading_indicators as lti
from src.live_trading_indicators.constants import TIME_TYPE, TIME_TYPE_UNIT, TIME_UNITS_IN_ONE_DAY


@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m, lti.Timeframe.t1h])
def test_live_1(config_default, test_source, a_symbol, timeframe):

    next_bar_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_bar_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 20:
        time.sleep(remain_time_sec)

    time_begin = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT) - timeframe.value
    indicators = lti.Indicators(test_source, time_begin)

    time.sleep(5)
    print(dt.datetime.utcnow())
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    print(len(ohlcv))

    n_bars = len(ohlcv.time)
    assert n_bars == 1

    time.sleep(5)
    print(dt.datetime.utcnow())
    ohlcv1 = indicators.OHLCV(a_symbol, timeframe)
    print(len(ohlcv1))

    assert ohlcv == ohlcv1


@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m])
def test_live_2(config_default, test_source, a_symbol, timeframe):

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 20:
        time.sleep(remain_time_sec)

    time_begin = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT) - timeframe.value * 2
    indicators = lti.Indicators(test_source, time_begin)

    time.sleep(5)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    assert len(ohlcv.time) == 2

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    time.sleep(remain_time_sec)

    time.sleep(5)
    ohlcv1 = indicators.OHLCV(a_symbol, timeframe)
    assert ohlcv == ohlcv1[:-1]


@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m])
def test_live_3(config_default, test_source, a_symbol, timeframe):

    print(dt.datetime.utcnow())
    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    print(f'{remain_time_sec=}')
    if remain_time_sec < 20:
        time.sleep(remain_time_sec)

    time_begin = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT) - TIME_UNITS_IN_ONE_DAY
    indicators = lti.Indicators(test_source, time_begin)

    time.sleep(9)
    print(dt.datetime.utcnow())
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    print(len(ohlcv))
    assert len(ohlcv.time) == TIME_UNITS_IN_ONE_DAY // timeframe.value

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    time.sleep(remain_time_sec)

    time.sleep(9)
    print(dt.datetime.utcnow())
    ohlcv1 = indicators.OHLCV(a_symbol, timeframe)
    print(len(ohlcv))
    assert ohlcv == ohlcv1[:-1]

