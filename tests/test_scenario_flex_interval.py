import pytest
import numpy as np
from src import live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_SECOND


def test_flex_1(clear_data, test_source, ohlcv_set):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    data_set = ohlcv_set[3]

    indicators = lti.Indicators(test_source, **clear_data)

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_begin + np.timedelta64(50, 'h'))

    n_bars = len(data_set[0])
    assert (ohlcv.time[:n_bars] == data_set[0]).all()
    assert (ohlcv.open[:n_bars] == data_set[1]).all()
    assert (ohlcv.high[:n_bars] == data_set[2]).all()
    assert (ohlcv.low[:n_bars] == data_set[3]).all()
    assert (ohlcv.close[:n_bars] == data_set[4]).all()
    assert (ohlcv.volume[:n_bars] == data_set[5]).all()


def test_flex_2(clear_data, test_source, ohlcv_set):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    data_set = ohlcv_set[3]

    indicators = lti.Indicators(test_source, **clear_data)

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin + np.timedelta64(1, 'h'), time_begin + np.timedelta64(1, 'h'))
    assert len(ohlcv.time) == 1
    assert ohlcv.time[0] == timeframe.begin_of_tf(time_begin + np.timedelta64(1, 'h'))

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_begin + np.timedelta64(50, 'h'))

    n_bars = len(data_set[0])
    assert (ohlcv.time[:n_bars] == data_set[0]).all()
    assert (ohlcv.open[:n_bars] == data_set[1]).all()
    assert (ohlcv.high[:n_bars] == data_set[2]).all()
    assert (ohlcv.low[:n_bars] == data_set[3]).all()
    assert (ohlcv.close[:n_bars] == data_set[4]).all()
    assert (ohlcv.volume[:n_bars] == data_set[5]).all()
