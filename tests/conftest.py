import pytest
import os.path as path
import pandas as pd
import numpy as np
from src.live_trading_indicators.constants import PRICE_TYPE, VOLUME_TYPE, TIME_TYPE
from src import live_trading_indicators as lti
import src.live_trading_indicators.datasources.binance as binance
import shutil
from src.live_trading_indicators.timeframe import Timeframe


@pytest.fixture
def test_source():
    return 'binance'


def test_symbols():

    symbols = []
    for symbol in ('btcusd', 'ethusd', 'etcusd'):
        symbols += [f'{symbol}t', f'um/{symbol}t', f'cm/{symbol}_perp']

    return symbols


def test_timeframes():
    timeframes = []
    for tf_str in ('1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'):
        timeframes += Timeframe.cast(tf_str)


def ohlcv_set(files, timeframe, symbol, date_start):

    dfs = []
    for file in files:
        filename = path.join('data', file)
        df = pd.read_csv(filename, header=None)
        if df[df.columns[0]].dtype != np.int64:
            df = pd.read_csv(filename)
        dfs.append(df)

    pd_data = pd.concat(dfs)

    use_timeframe = Timeframe.cast(timeframe)
    time = pd_data[df.columns[0]].to_numpy(TIME_TYPE)
    open = pd_data[df.columns[1]].to_numpy(PRICE_TYPE)
    high = pd_data[df.columns[2]].to_numpy(PRICE_TYPE)
    low = pd_data[df.columns[3]].to_numpy(PRICE_TYPE)
    close = pd_data[df.columns[4]].to_numpy(PRICE_TYPE)
    volume = pd_data[df.columns[5]].to_numpy(VOLUME_TYPE)
    return (symbol, use_timeframe, date_start, (time, open, high, low, close, volume))


def pytest_generate_tests(metafunc):

    if 'test_symbol' in metafunc.fixturenames:
        return metafunc.parametrize('a_symbol', test_symbols())

    if 'test_timeframe' in metafunc.fixturenames:
        return metafunc.parametrize("a_timeframe", test_timeframes())

    if 'ohlcv_set' in metafunc.fixturenames:
        return metafunc.parametrize('ohlcv_set', [ohlcv_set(['ETHUSDT-1h-2022-08-24.zip'], '1h', 'um/ethusdt', '2022-08-24'),
                ohlcv_set(['ETHUSDT-1h-2022-08-25.zip'], '1h', 'um/ethusdt', '2022-08-25'),
                ohlcv_set(['ETHUSDT-1h-2022-08-24.zip', 'ETHUSDT-1h-2022-08-25.zip'], '1h', 'um/ethusdt', '2022-08-24'),

                ohlcv_set(['BTCUSDT-1h-2022-09-07.zip'], '1h', 'btcusdt', '2022-09-07'),
                ohlcv_set(['BTCUSDT-1h-2022-09-08.zip'], '1h', 'btcusdt', '2022-09-08'),
                ohlcv_set(['BTCUSDT-1h-2022-09-07.zip', 'BTCUSDT-1h-2022-09-08.zip'], '1h', 'btcusdt', '2022-09-07'),

                ohlcv_set(['BTCUSD_PERP-1m-2022-10-24.zip'], '1m', 'cm/btcusd_perp', '2022-10-24'),
                ohlcv_set(['BTCUSD_PERP-1m-2022-10-25.zip'], '1m', 'cm/btcusd_perp', '2022-10-25'),
                ohlcv_set(['BTCUSD_PERP-1m-2022-10-24.zip', 'BTCUSD_PERP-1m-2022-10-25.zip'], '1m', 'cm/btcusd_perp', '2022-10-24')])


@pytest.fixture
def clear_data():  # source_type: ticks

    data_path = 'test_data'
    cash_folder = path.join(data_path, 'timeframe_data')
    sources_folder = path.join(data_path, 'sources')

    lti.config('set_default')

    shutil.rmtree(data_path, ignore_errors=True)
    yield {
        'cash_folder' : cash_folder,
        'sources_folder': sources_folder
    }
    shutil.rmtree(data_path, ignore_errors=True)


@pytest.fixture
def config_default():
    lti.config('set_default')

