import pytest
import src.fast_trading_indicators as fti
import shutil

SOURCE = 'binance_ticks'
SYMBOL = 'um/ethusdt'


@pytest.fixture
def default_source():
    return SOURCE


@pytest.fixture
def default_symbol():
    return SYMBOL


@pytest.fixture
def clear_data():
    common_data_path = 'test_data'
    shutil.rmtree(common_data_path, ignore_errors=True)
    yield common_data_path
    shutil.rmtree(common_data_path, ignore_errors=True)
