import pytest
import numpy as np
from src import live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time


def test_fix_wo_time(clear_data, test_source, ohlcv_set):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    data_set = ohlcv_set[3]

    time_end = time_begin + np.timedelta64(50, 'h')
    indicators = lti.Indicators(test_source, time_begin, time_end, **clear_data)
    count_file_load = indicators.source_data.count_file_load
    count_datasource_get = indicators.source_data.count_datasource_get

    ohlcv = indicators.OHLCV(symbol, timeframe)

    assert ohlcv.time[-1] == ohlcv.end_bar_time
    assert ohlcv.end_bar_time == timeframe.begin_of_tf(time_end)

    n_bars = len(data_set[0])
    assert (ohlcv.time[:n_bars] == data_set[0]).all()
    assert (ohlcv.open[:n_bars] == data_set[1]).all()
    assert (ohlcv.high[:n_bars] == data_set[2]).all()
    assert (ohlcv.low[:n_bars] == data_set[3]).all()
    assert (ohlcv.close[:n_bars] == data_set[4]).all()
    assert (ohlcv.volume[:n_bars] == data_set[5]).all()

    assert count_file_load == indicators.source_data.count_file_load
    assert count_datasource_get != indicators.source_data.count_datasource_get

    # No load, no get
    count_file_load = indicators.source_data.count_file_load
    count_datasource_get = indicators.source_data.count_datasource_get
    ohlcv = indicators.OHLCV(symbol, timeframe)
    assert count_file_load == indicators.source_data.count_file_load
    assert count_datasource_get == indicators.source_data.count_datasource_get

    # Load, no get
    indicators = lti.Indicators(test_source, time_begin, time_end, **clear_data)
    count_file_load = indicators.source_data.count_file_load
    count_datasource_get = indicators.source_data.count_datasource_get
    ohlcv = indicators.OHLCV(symbol, timeframe)
    assert count_file_load != indicators.source_data.count_file_load
    assert count_datasource_get == indicators.source_data.count_datasource_get


def test_fix_with_time(clear_data, test_source, ohlcv_set):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    data_set = ohlcv_set[3]

    indicators = lti.Indicators(test_source, time_begin - np.timedelta64(30), time_begin + np.timedelta64(50, 'h'), **clear_data)

    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin, time_begin + len(data_set[0]) * timeframe.value - 1)

    n_bars = len(data_set[0])
    assert (ohlcv.time == data_set[0]).all()
    assert (ohlcv.open == data_set[1]).all()
    assert (ohlcv.high == data_set[2]).all()
    assert (ohlcv.low == data_set[3]).all()
    assert (ohlcv.close == data_set[4]).all()
    assert (ohlcv.volume == data_set[5]).all()

    count_file_load = indicators.source_data.count_file_load
    count_datasource_get = indicators.source_data.count_datasource_get
    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin + timeframe.value, time_begin + 2 * timeframe.value)
    assert count_file_load == indicators.source_data.count_file_load
    assert count_datasource_get == indicators.source_data.count_datasource_get


def test_fix_wo_time_many_symbols(config_default, test_source, a_symbol):

    indicators = lti.Indicators(test_source, 20220701, 20220705)

    ohlcv = indicators.OHLCV(a_symbol, '1m')

