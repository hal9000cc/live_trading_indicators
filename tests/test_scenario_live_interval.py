import pytest
import numpy as np
import datetime as dt
import time
from src import live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time
from src.live_trading_indicators.constants import TIME_TYPE, TIME_TYPE_UNIT


@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m, lti.Timeframe.t1h])
def test_fix_wo_live_with_incomplete_1(config_default, test_source, a_symbol, timeframe):

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(int)
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


def test_fix_wo_live_with_incomplete_2(config_default, test_source, a_symbol):

    timeframe = lti.Timeframe.t1m

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(int)
    if remain_time_sec < 10: time.sleep(remain_time_sec)

    now = dt.datetime.utcnow()
    time_begin = np.datetime64(now, 'D')
    indicators = lti.Indicators(test_source, time_begin, with_incomplete_bar=True)

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
