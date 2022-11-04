import pytest
import numpy as np
from src import live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_SECOND, TIME_UNITS_IN_ONE_DAY, TIME_TYPE_UNIT


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

    time_begin1 = time_begin + timeframe.value + 1
    time_end1 = time_begin + np.timedelta64(50, 'h') - 1
    count_file_load = indicators.source_data.count_file_load
    count_datasource_get = indicators.source_data.count_datasource_get
    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin1, time_end1)
    assert count_file_load == indicators.source_data.count_file_load #
    assert count_datasource_get == indicators.source_data.count_datasource_get #
    assert ohlcv.time[0] == timeframe.begin_of_tf(time_begin1)
    assert ohlcv.time[-1] == timeframe.begin_of_tf(time_end1)

    time_begin1 = time_begin + timeframe.value + 1
    time_end1 = time_begin + np.timedelta64(50, 'h') + timeframe.value
    count_file_load = indicators.source_data.count_file_load
    count_datasource_get = indicators.source_data.count_datasource_get
    ohlcv = indicators.OHLCV(symbol, timeframe, time_begin1, time_end1)
    assert indicators.source_data.count_file_load == count_file_load #
    assert indicators.source_data.count_datasource_get == count_datasource_get #
    assert ohlcv.time[0] == timeframe.begin_of_tf(time_begin1)
    assert ohlcv.time[-1] == timeframe.begin_of_tf(time_end1)


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


@pytest.mark.parametrize('symbol', ['ethusdt', 'um/ethusdt', 'cm/ethusd_perp'])
def test_flex_3(clear_data, test_source, symbol, a_timeframe_short):

    date = np.datetime64('2022-07-01')

    indicators = lti.Indicators(test_source, **clear_data)
    ohlcv = indicators.OHLCV(symbol, a_timeframe_short, date, date)
    assert len(ohlcv.time) == TIME_UNITS_IN_ONE_DAY / a_timeframe_short.value
    assert ohlcv.time[0] == date
    assert ohlcv.time[-1] == a_timeframe_short.begin_of_tf(np.datetime64(date + 1, TIME_TYPE_UNIT) - 1)

    ohlcv1 = indicators.OHLCV(symbol, a_timeframe_short, date, date + 1)
    assert len(ohlcv1.time) == TIME_UNITS_IN_ONE_DAY / a_timeframe_short.value * 2
    assert ohlcv1.time[0] == date
    assert ohlcv1.time[-1] == a_timeframe_short.begin_of_tf(np.datetime64(date + 2, TIME_TYPE_UNIT) - 1)
    assert ohlcv == ohlcv1[:len(ohlcv)]

    indicators = lti.Indicators(test_source, **clear_data)
    ohlcv2 = indicators.OHLCV(symbol, a_timeframe_short, date, date)
    assert ohlcv2 == ohlcv

    ohlcv3 = indicators.OHLCV(symbol, a_timeframe_short, date, date + 1)
    assert ohlcv3 == ohlcv1

    ohlcv4 = indicators.OHLCV(symbol, a_timeframe_short, date, date + 2)
    assert len(ohlcv4.time) == TIME_UNITS_IN_ONE_DAY / a_timeframe_short.value * 3
    assert ohlcv4.time[0] == date
    assert ohlcv4.time[-1] == a_timeframe_short.begin_of_tf(np.datetime64(date + 3, TIME_TYPE_UNIT) - 1)
    assert ohlcv3 == ohlcv4[:len(ohlcv3)]


@pytest.mark.parametrize('symbol', ['ethusdt', 'um/ethusdt', 'cm/ethusd_perp'])
def test_flex_4(clear_data, test_source, symbol, a_timeframe_short):

    offset = TIME_UNITS_IN_ONE_SECOND * 60 * 60 + 50
    date = np.datetime64('2022-07-01', TIME_TYPE_UNIT)
    date_b = a_timeframe_short.begin_of_tf(date + offset)

    indicators = lti.Indicators(test_source, **clear_data)
    ohlcv = indicators.OHLCV(symbol, a_timeframe_short, date + offset, a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY) - 1)
    assert len(ohlcv.time) == TIME_UNITS_IN_ONE_DAY / a_timeframe_short.value
    assert ohlcv.time[0] == date_b
    assert ohlcv.time[-1] == a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY) - a_timeframe_short.value

    ohlcv1 = indicators.OHLCV(symbol, a_timeframe_short, date + offset, a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY * 2) - 1)
    assert len(ohlcv1.time) == TIME_UNITS_IN_ONE_DAY / a_timeframe_short.value * 2
    assert ohlcv1.time[0] == date_b
    assert ohlcv1.time[-1] == a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY * 2) - a_timeframe_short.value
    assert ohlcv == ohlcv1[:len(ohlcv)]

    indicators = lti.Indicators(test_source, **clear_data)
    ohlcv2 = indicators.OHLCV(symbol, a_timeframe_short, date + offset, a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY) - 1)
    assert ohlcv2 == ohlcv

    ohlcv3 = indicators.OHLCV(symbol, a_timeframe_short, date + offset, a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY * 2) - 1)
    assert ohlcv3 == ohlcv1

    ohlcv4 = indicators.OHLCV(symbol, a_timeframe_short, date + offset, a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY * 3) - 1)
    assert len(ohlcv4.time) == TIME_UNITS_IN_ONE_DAY / a_timeframe_short.value * 3
    assert ohlcv4.time[0] == date_b
    assert ohlcv4.time[-1] == a_timeframe_short.begin_of_tf(date + offset + TIME_UNITS_IN_ONE_DAY * 3) - a_timeframe_short
    assert ohlcv3 == ohlcv4[:len(ohlcv3)]


@pytest.mark.parametrize('symbol', ['ethusdt', 'um/ethusdt', 'cm/ethusd_perp'])
def test_flex_5(config_default, test_source, symbol, a_timeframe_short):

    indicators = lti.Indicators('binance')
    sma15 = indicators.SMA(symbol, '1h', 20220905, 20220915, period=15)

