import pytest
import numpy as np
from src import live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time


def test_fix_wo_time_1(clear_data, test_source, ohlcv_set):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    data_set = ohlcv_set[3]

    print(ohlcv_set)
    indicators = lti.Indicators(test_source, time_begin, time_begin + np.timedelta64(50, 'h'), **clear_data)

    ohlcv = indicators.OHLCV(symbol, timeframe)

    n_bars = len(data_set[0])
    assert (ohlcv.time[:n_bars] == data_set[0]).all()
    assert (ohlcv.open[:n_bars] == data_set[1]).all()
    assert (ohlcv.high[:n_bars] == data_set[2]).all()
    assert (ohlcv.low[:n_bars] == data_set[3]).all()
    assert (ohlcv.close[:n_bars] == data_set[4]).all()
    assert (ohlcv.volume[:n_bars] == data_set[5]).all()



# def test_fix_wo_time_2(test_source, test_symbol, test_timeframe, date_begin, date_end):
#
#     indicators = lti.Indicators(test_source, date_begin, date_end)
#
#     macd = indicators.MACD(test_symbol, test_timeframe, short=17, long=25, signal=5)
#     ohlcv = indicators.OHLCV(test_symbol, test_timeframe)
#
#
# def test_fix_with_time_1(test_source, test_symbol, test_timeframe, date_begin, date_end):
#     indicators = lti.Indicators(test_source, date_begin, date_end)
#
#     ohlcv = indicators.OHLCV(test_symbol, test_timeframe, time_begin, time_end)
#     macd = indicators.MACD(test_symbol, test_timeframe, time_begin, time_end, short=17, long=25, signal=5)
#
#     n_bars_in_day = 24 * 60 * 60 // test_timeframe.value
#     verify_day(ohlcv[: n_bars_in_day], date_begin, test_symbol)
#     verify_day(ohlcv[-n_bars_in_day:], date_end, test_symbol)
#
#
# def test_fix_with_time_2(test_source, test_symbol, test_timeframe, date_begin, date_end):
#     indicators = lti.Indicators(test_source, date_begin, date_end)
#
#     macd = indicators.MACD(test_symbol, test_timeframe, time_begin, time_end, short=17, long=25, signal=5)
#     ohlcv = indicators.OHLCV(test_symbol, test_timeframe, time_begin, time_end)
#
#     n_bars_in_day = 24 * 60 * 60 // test_timeframe.value
#     verify_day(ohlcv[: n_bars_in_day], date_begin, test_symbol)
#     verify_day(ohlcv[-n_bars_in_day:], date_end, test_symbol)
#
