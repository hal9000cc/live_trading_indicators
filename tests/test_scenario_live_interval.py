import pytest
import numpy as np
import datetime as dt
import time
from src import live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time


def test_fix_wo_live_1(config_default, test_source, a_symbol):

    time_begin = dt.datetime.utcnow()
    indicators = lti.Indicators(test_source, time_begin)

    ohlcv = indicators.OHLCV(a_symbol, '1h')

    n_bars = len(ohlcv.time)
    assert n_bars == 1


def test_fix_wo_live_2(config_default, test_source, a_symbol):

    timeframe = lti.Timeframe.t1m

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(int)
    if remain_time_sec < 10: time.sleep(remain_time_sec)

    now = dt.datetime.utcnow()
    time_begin = np.datetime64(now, 'D')
    indicators = lti.Indicators(test_source, time_begin)

    ohlcv = indicators.OHLCV(a_symbol, timeframe)

    n_bars = len(ohlcv.time)
    assert n_bars == np.datetime64(now, 'm') - np.datetime64(time_begin, 'm') + 1

    next_time = timeframe.begin_of_tf(now) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(int)

    if remain_time_sec > 0: time.sleep(remain_time_sec)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    assert len(ohlcv.time) == n_bars or len(ohlcv.time) == n_bars + 1

    time.sleep(2)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    assert len(ohlcv.time) == n_bars + 1
