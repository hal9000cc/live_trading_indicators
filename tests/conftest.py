import os

import pytest
import os.path as path
import src.fast_trading_indicators as fti
import shutil

SOURCE = 'binance'
SYMBOL = 'um/ethusdt'
TIMEFRAME = fti.Timeframe.t1h


@pytest.fixture
def default_source():
    return SOURCE


@pytest.fixture
def default_symbol():
    return SYMBOL


@pytest.fixture
def default_timeframe():
    return TIMEFRAME


@pytest.fixture
def config_clear_data():

    data_path = 'test_data'
    cash_folder = path.join(data_path, 'timeframe_data')
    sources_folder = path.join(data_path, 'sources')

    fti.config(cash_folder=cash_folder, sources_folder=sources_folder)

    shutil.rmtree(data_path, ignore_errors=True)
    yield data_path
    shutil.rmtree(data_path, ignore_errors=True)

@pytest.fixture
def config_default():
    fti.config('set_default')
