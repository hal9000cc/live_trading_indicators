import pytest
import os.path as path
import src.fast_trading_indicators as fti
import src.fast_trading_indicators.datasources.binance as binance
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
def config_clear_data_t():  # source_type: ticks

    data_path = 'test_data'
    cash_folder = path.join(data_path, 'timeframe_data')
    sources_folder = path.join(data_path, 'sources')

    fti.config('set_default')

    shutil.rmtree(data_path, ignore_errors=True)
    yield {
        'cash_folder' : cash_folder,
        'sources_folder': sources_folder,
        'source_type': 'ticks'
    }
    shutil.rmtree(data_path, ignore_errors=True)


@pytest.fixture
def config_clear_data_b():  # source_type: bars

    data_path = 'test_data'
    cash_folder = path.join(data_path, 'timeframe_data')
    sources_folder = path.join(data_path, 'sources')

    fti.config('set_default')

    shutil.rmtree(data_path, ignore_errors=True)
    yield {
        'cash_folder' : cash_folder,
        'sources_folder': sources_folder,
        'source_type': 'bars'
    }
    shutil.rmtree(data_path, ignore_errors=True)


@pytest.fixture
def config_default():  # source: ticks
    fti.config('set_default')


@pytest.fixture
def config_default_t():  # source: ticks
    fti.config('set_default')
    yield {'source_type': 'ticks'}


def pytest_generate_tests(metafunc):

    if 'all_symbols' not in metafunc.fixturenames:
        return

    all_symbols = []
    for part in ('um', 'cm', 'spot'):
        binance.download_exchange_info_part(part)
        for symbol_name in binance.exchange_info_data[part]['symbols'].keys():
            symbol = ('' if part == 'spot' else part + '/') + symbol_name
            all_symbols.append(symbol)

    return metafunc.parametrize("all_symbols", all_symbols)
