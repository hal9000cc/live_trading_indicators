import pytest
import numpy as np
import datetime as dt
import time
import live_trading_indicators as lti
from live_trading_indicators.constants import TIME_TYPE, TIME_TYPE_UNIT


LIVE_ACTIVE_SYMBOLS = ['btcusdt', 'ethusdt', 'um/btcusdt', 'um/ethusdt', 'cm/btcusd_perp', 'cm/ethusd_perp']
LIVE_ACTIVE_UM_SYMBOLS = ['um/btcusdt', 'um/ethusdt']
LIVE_VOLUME_CHANGE_RETRY_COUNT = 6
LIVE_VOLUME_CHANGE_RETRY_DELAY_SEC = 5


@pytest.mark.slow
@pytest.mark.parametrize('live_symbol', LIVE_ACTIVE_SYMBOLS)
@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1m, lti.Timeframe.t1h])
def test_fix_live_with_incomplete_1(config_default, test_source, live_symbol, timeframe):

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 10:
        time.sleep(remain_time_sec + 10)

    time_begin = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT) - timeframe.value
    indicators = lti.Indicators(test_source, time_begin, with_incomplete_bar=True, **config_default)

    while True:
        ohlcv = indicators.OHLCV(live_symbol, timeframe)
        if len(ohlcv.time) == 2: break
        assert len(ohlcv.time) == 1

    n_bars = len(ohlcv.time)
    assert n_bars == 2

    time.sleep(5)
    ohlcv1 = indicators.OHLCV(live_symbol, timeframe)
    assert ohlcv.volume[n_bars - 1] <= ohlcv1.volume[n_bars - 1]


@pytest.mark.slow
@pytest.mark.parametrize('live_symbol', LIVE_ACTIVE_SYMBOLS)
def test_fix_live_with_incomplete_2(config_default, test_source, live_symbol):

    timeframe = lti.Timeframe.t1m

    next_time = timeframe.begin_of_tf(dt.datetime.utcnow()) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 30:
        time.sleep(remain_time_sec + 10)

    now = dt.datetime.utcnow()
    time_begin = np.datetime64(now, 'D')
    indicators = lti.Indicators(test_source, time_begin, with_incomplete_bar=True, **config_default)

    ohlcv = indicators.OHLCV(live_symbol, timeframe)

    n_bars = len(ohlcv.time)
    assert n_bars == (np.datetime64(now, 'm') - np.datetime64(time_begin, 'm')).astype(np.int64) + 1

    next_time = timeframe.begin_of_tf(now) + timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)

    if remain_time_sec > 0:
        time.sleep(remain_time_sec)
    ohlcv = indicators.OHLCV(live_symbol, timeframe)
    assert len(ohlcv.time) == n_bars or len(ohlcv.time) == n_bars + 1

    time.sleep(10)
    ohlcv = indicators.OHLCV(live_symbol, timeframe)
    assert len(ohlcv.time) == n_bars + 1


@pytest.mark.slow
@pytest.mark.parametrize('live_um_symbol', LIVE_ACTIVE_UM_SYMBOLS)
def test_fix_live_with_incomplete_3(config_default, test_source, live_um_symbol, a_timeframe):

    next_time = a_timeframe.begin_of_tf(dt.datetime.utcnow()) + a_timeframe.value
    remain_time_sec = (np.datetime64(next_time, 's') - np.datetime64(dt.datetime.utcnow(), 's')).astype(np.int64)
    if remain_time_sec < 30:
        time.sleep(remain_time_sec + 5)

    now = dt.datetime.utcnow()
    time_begin = np.datetime64(now, 'D')
    indicators = lti.Indicators(test_source, time_begin, with_incomplete_bar=True, **config_default)

    ohlcv = indicators.OHLCV(live_um_symbol, a_timeframe)
    n_bars = len(ohlcv.time)
    volume_before = ohlcv.volume[n_bars - 1]

    for _ in range(LIVE_VOLUME_CHANGE_RETRY_COUNT):
        time.sleep(LIVE_VOLUME_CHANGE_RETRY_DELAY_SEC)
        ohlcv1 = indicators.OHLCV(live_um_symbol, a_timeframe)
        assert ohlcv.time[n_bars - 1] == ohlcv1.time[n_bars - 1]
        if ohlcv1.volume[n_bars - 1] != volume_before:
            break

    assert ohlcv1.volume[n_bars - 1] != volume_before
