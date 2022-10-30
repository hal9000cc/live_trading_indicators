import pytest
import numpy as np
from src import live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time


@pytest.mark.parametrize('request_bar_limit', [500, 1500])
def test_fix_wo_time(clear_data, test_source, ohlcv_set, request_bar_limit):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    data_set = ohlcv_set[3]

    indicators = lti.Indicators(test_source, time_begin, time_begin + np.timedelta64(50, 'h'), **clear_data|{'request_bar_limit': request_bar_limit})

    ohlcv = indicators.OHLCV(symbol, timeframe)

    n_bars = len(data_set[0])
    assert (ohlcv.time[:n_bars] == data_set[0]).all()
    assert (ohlcv.open[:n_bars] == data_set[1]).all()
    assert (ohlcv.high[:n_bars] == data_set[2]).all()
    assert (ohlcv.low[:n_bars] == data_set[3]).all()
    assert (ohlcv.close[:n_bars] == data_set[4]).all()
    assert (ohlcv.volume[:n_bars] == data_set[5]).all()


def test_fix_with_time(clear_data, test_source, ohlcv_set):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    data_set = ohlcv_set[3]

    print(ohlcv_set)
    indicators = lti.Indicators(test_source, time_begin - np.timedelta64(30), time_begin + np.timedelta64(50, 'h'), **clear_data)

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_begin + np.timedelta64(50, 'h'))

    n_bars = len(data_set[0])
    assert (ohlcv.time[:n_bars] == data_set[0]).all()
    assert (ohlcv.open[:n_bars] == data_set[1]).all()
    assert (ohlcv.high[:n_bars] == data_set[2]).all()
    assert (ohlcv.low[:n_bars] == data_set[3]).all()
    assert (ohlcv.close[:n_bars] == data_set[4]).all()
    assert (ohlcv.volume[:n_bars] == data_set[5]).all()


def test_fix_wo_time_many_symbols(config_default, test_source, a_symbol):

    indicators = lti.Indicators(test_source, 20220701, 20220705)

    ohlcv = indicators.OHLCV(a_symbol, '1m')

