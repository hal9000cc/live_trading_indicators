import pytest
import os
import datetime as dt
import numpy as np
from common_test import *
from src import live_trading_indicators as lti
from src.live_trading_indicators.constants import TIME_TYPE_UNIT, TIME_UNITS_IN_ONE_DAY
from src.live_trading_indicators.timeframe import Timeframe
from src.live_trading_indicators.exceptions import *


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-01-01', '2022-01-10')
])
def test_1d_load(clear_data, test_source, test_symbol, time_begin, time_end):
    timeframe = '1d'

    indicators = lti.Indicators('binance', time_begin, time_end, **clear_data)

    ohlcv = indicators.OHLCV(test_symbol, timeframe)

    assert len(ohlcv) == np.datetime64(time_end, 'D') - np.datetime64(time_begin, 'D') + 1


def test_hole_load(clear_data, test_source, test_symbol, a_timeframe):

    indicators = lti.Indicators('binance', **clear_data)
    ohlcv0102 = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-01', '2022-07-02')
    ohlcv06 = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-06', '2022-07-06')

    indicators = lti.Indicators('binance', **clear_data)
    ohlcv = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-01', '2022-07-06')

    assert ohlcv[: np.datetime64('2022-07-03', TIME_TYPE_UNIT)] == ohlcv0102
    assert ohlcv[np.datetime64('2022-07-06', TIME_TYPE_UNIT): ] == ohlcv06


# @pytest.mark.parametrize('timeframe, symbol', [
#     (Timeframe.t5m, 'um/ethusdt')
# ])
# def test_save_intermediate(clear_data, test_source, symbol, timeframe):
#
#     indicators = lti.Indicators('binance', **clear_data)
#
#     indicators.OHLCV(symbol, timeframe, 20220701, 20220820)
#
#     store_path = os.path.join('test_data', 'timeframe_data', test_source, symbol.split('/')[0])
#     mt1 = os.path.getmtime(os.path.join(store_path, f'{symbol.split("/")[1]}-{timeframe!s}-2022-07.ltc'))
#     mt2 = os.path.getmtime(os.path.join(store_path, f'{symbol.split("/")[1]}-{timeframe!s}-2022-08.ltc'))
#     t1, t2 = dt.datetime.fromtimestamp(mt1), dt.datetime.fromtimestamp(mt2)
#
#     assert (t2 - t1).total_seconds() > 1


@pytest.mark.parametrize('timeframe, symbol', [
    (Timeframe.t15m, 'um/ethusdt')
])
def test_download_over_end(clear_data, test_source, symbol, timeframe):

    indicators = lti.Indicators('binance', **clear_data)

    now = np.datetime64(dt.datetime.utcnow(), 'D')

    with pytest.raises(LTIExceptionOutOfThePeriod):
        ohlcv = indicators.OHLCV(symbol, timeframe, now - 2, now + 10)

    ohlcv = indicators.OHLCV(symbol, timeframe, now - 3, now - 1)


def test_store(clear_data, test_source, test_symbol, a_timeframe):

    indicators = lti.Indicators('binance', **clear_data)
    ohlcv = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-01', '2022-07-02').copy()

    indicators = lti.Indicators('binance', **clear_data)
    ohlcv1 = indicators.OHLCV(test_symbol, a_timeframe, '2022-07-01', '2022-07-02').copy()

    assert ohlcv == ohlcv1


@pytest.mark.parametrize('symbol, timeframe', [
    ('ethusdt', '1d')
])
def test_2020_year(clear_data, test_source, symbol, timeframe):

    indicators = lti.Indicators(test_source, **clear_data)
    ohlcv = indicators.OHLCV(symbol, timeframe, 20200101, 20201231)
    assert len(ohlcv) == 366

    indicators = lti.Indicators(test_source, **clear_data)
    ohlcv = indicators.OHLCV(symbol, timeframe, 20200101, 20201231)
    assert len(ohlcv) == 366


@pytest.mark.parametrize('symbol, timeframe', [
    ('btcusdt', '1h')
])
def test_2020_year_h(test_source, symbol, timeframe):

    indicators = lti.Indicators(test_source, log_level='DEBUG')
    ohlcv = indicators.OHLCV(symbol, timeframe, 20220101, 20221231)


@pytest.mark.parametrize('symbol, date', [
    ('um/btcusdt', '2017-01-01'),
    ('um/etcusdt', '2020-01-01'),
#    ('um/etcusdt', '2020-01-16')
])
def test_empty_day(clear_data, symbol, date):

    indicators = lti.Indicators('binance', restore_empty_bars=False, **clear_data)
    ohlcv1 = indicators.OHLCV(symbol, '1h', date, date)
    assert indicators.source_data.count_file_load == 0
    assert indicators.source_data.count_datasource_get == 1
    assert indicators.source_data.count_datasource_bars_get == 0

    indicators = lti.Indicators('binance', restore_empty_bars=False, **clear_data)
    ohlcv2 = indicators.OHLCV(symbol, '1h', date, date)
    assert indicators.source_data.count_file_load == 1
    assert indicators.source_data.count_datasource_get == 0
    assert indicators.source_data.count_datasource_bars_get == 0

    assert ohlcv1 == ohlcv2
    assert ohlcv1.empty_bars_count == 24
    assert ohlcv1.empty_bars_fraction == 1


@pytest.mark.parametrize('symbol, date', [
    ('um/btcusdt', '2017-01-01'),
    ('um/etcusdt', '2020-01-01'),
    ('um/etcusdt', '2020-01-16'),
    ('um/etcusdt', '2017-01-16'),
    ('um/etcusdt', '2022-01-16')
])
def test_empty_identical_empty(clear_data, symbol, date):

    indicators = lti.Indicators('binance', restore_empty_bars=False, **clear_data)
    ohlcv1 = indicators.OHLCV(symbol, '1h', date, date)

    indicators = lti.Indicators('binance', restore_empty_bars=False, **clear_data)
    ohlcv2 = indicators.OHLCV(symbol, '1h', date, date)

    assert ohlcv1 == ohlcv2
    assert ohlcv1.empty_bars_count == ohlcv2.empty_bars_count
    assert ohlcv1.empty_bars_fraction == ohlcv2.empty_bars_fraction


def test_data_skips(clear_data):

    timeframe = '5m'
    clear_data['restore_empty_bars'] = False
    indicators = lti.Indicators('binance', '2018-07-04', '2018-07-04', **clear_data)

    ohlcv = indicators.OHLCV('btcusdt', timeframe)
    assert np.isnan(ohlcv.close).any()

    clear_data['restore_empty_bars'] = True
    indicators = lti.Indicators('binance', '2018-07-04', '2018-07-04', **clear_data)

    ohlcv = indicators.OHLCV('btcusdt', timeframe)
    assert not np.isnan(ohlcv.close).any()

