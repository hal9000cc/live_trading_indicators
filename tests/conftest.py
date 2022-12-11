import ccxt
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


@pytest.fixture
def test_symbol():
    return 'um/ethusdt'


def all_symbols():

    symbols = []
    for part in ('um', 'cm', 'spot'):
        binance.download_exchange_info_part(part)
        for symbol_name in binance.exchange_info_data[part]['symbols'].keys():
            symbol = ('' if part == 'spot' else part + '/') + symbol_name
            symbols.append(symbol)

    return symbols


def test_symbols():

    symbols = []
    for symbol in ('btcusd', 'ethusd', 'etcusd'):
        symbols += [f'{symbol}t', f'um/{symbol}t', f'cm/{symbol}_perp']

    symbols.append('um/stmxusdt')
    return symbols


def test_ccxt_symbols():
    return ['BTC/USDT', 'ETH/USDT', 'ETC/USDT']


def test_ccxt_sources():

    exchanges = []
    #testing_exchanges = set(ccxt.exchanges)
        # - {'bibox', 'binancecoinm', 'binanceus', 'bitbay', 'btcbox', 'mexc3', 'coinone', 'mercado', 'okx', 'kuna',
        #    'bitforex', 'huobijp', 'okcoin'}

    for exchange_name in ccxt.exchanges:
        exchange = getattr(ccxt, exchange_name)()
        if exchange.has['fetchOHLCV']:
            exchanges.append(exchange_name)

    return exchanges


def test_timeframes():

    timeframes = []
    for tf_str in ('1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'):
        timeframes.append(Timeframe.cast(tf_str))

    return timeframes


def test_big_timeframes():

    timeframes = []
    for tf_str in ('1h', '2h', '4h', '6h', '8h', '12h', '1d'):
        timeframes.append(Timeframe.cast(tf_str))

    return timeframes


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
    return (symbol, use_timeframe, date_start, (time, open, high, low, close, volume), pd_data)


def pytest_generate_tests(metafunc):

    if 'a_symbol' in metafunc.fixturenames:
        metafunc.parametrize('a_symbol', test_symbols())

    if 'a_ccxt_symbol' in metafunc.fixturenames:
        metafunc.parametrize('a_ccxt_symbol', test_ccxt_symbols())

    if 'a_ccxt_source' in metafunc.fixturenames:
        metafunc.parametrize('a_ccxt_source', test_ccxt_sources())

    if 'a_timeframe' in metafunc.fixturenames:
        metafunc.parametrize("a_timeframe", test_timeframes())

    if 'a_big_timeframe' in metafunc.fixturenames:
        metafunc.parametrize("a_big_timeframe", test_big_timeframes())

    if 'a_timeframe_short' in metafunc.fixturenames:
        metafunc.parametrize("a_timeframe_short", [Timeframe.t1m, Timeframe.t1h, Timeframe.t12h, Timeframe.t1d])

    if 'ohlcv_set' in metafunc.fixturenames:
        metafunc.parametrize('ohlcv_set', [

                ohlcv_set(['BTCUSDT-1m-2022-09-05.zip'], '1m', 'um/btcusdt', '2022-09-05'),
                ohlcv_set(['BTCUSDT-1m-2022-09-06.zip'], '1m', 'um/btcusdt', '2022-09-06'),
                ohlcv_set(['BTCUSDT-1m-2022-09-05.zip', 'BTCUSDT-1m-2022-09-06.zip'], '1m', 'um/btcusdt', '2022-09-05'),

                ohlcv_set(['ETHUSDT-1m-2022-08-14.zip'], '1m', 'ethusdt', '2022-08-14'),
                ohlcv_set(['ETHUSDT-1m-2022-08-15.zip'], '1m', 'ethusdt', '2022-08-15'),
                ohlcv_set(['ETHUSDT-1m-2022-08-14.zip', 'ETHUSDT-1m-2022-08-15.zip'], '1m', 'ethusdt', '2022-08-14'),

                ohlcv_set(['ETHUSDT-1h-2022-08-24.zip'], '1h', 'um/ethusdt', '2022-08-24'),
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
    cache_folder = path.join(data_path, 'timeframe_data')
    sources_folder = path.join(data_path, 'sources')

    lti.config('set_default')

    shutil.rmtree(data_path, ignore_errors=True)
    yield {
        'cache_folder' : cache_folder,
        'sources_folder': sources_folder,
        'log_level': 'INFO'
    }
    shutil.rmtree(data_path, ignore_errors=True)


@pytest.fixture
def empty_test_folder():
    test_folder = path.join('test_data', 'empty_folder')
    shutil.rmtree(test_folder, ignore_errors=True)
    yield test_folder
    shutil.rmtree(test_folder, ignore_errors=True)


@pytest.fixture
def config_default():
    lti.config('set_default')
    return {'log_level': 'CRITICAL'}
    #return {}

