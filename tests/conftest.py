import pytest
import os.path as path
import src.live_trading_indicators as lti
import src.live_trading_indicators.datasources.binance as binance
import shutil

SOURCE = 'binance'
SYMBOL = 'um/ethusdt'
TIMEFRAME = lti.Timeframe.t1h


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

    lti.config('set_default')

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

    lti.config('set_default')

    shutil.rmtree(data_path, ignore_errors=True)
    yield {
        'cash_folder' : cash_folder,
        'sources_folder': sources_folder,
        'source_type': 'bars'
    }
    shutil.rmtree(data_path, ignore_errors=True)


@pytest.fixture
def config_default():  # source: ticks
    lti.config('set_default')


@pytest.fixture
def config_default_t():  # source: ticks
    lti.config('set_default')
    yield {'source_type': 'ticks'}


def generate_all_symbols():

    all_symbols = []
    # for part in ('um', 'cm', 'spot'):
    #     binance.download_exchange_info_part(part)
    #     for symbol_name in binance.exchange_info_data[part]['symbols'].keys():
    #         symbol = ('' if part == 'spot' else part + '/') + symbol_name
    #         all_symbols.append(symbol)

    for symbol in ('btcusd', 'ethusd', 'btcusd'):
        all_symbols += [f'{symbol}t', f'um/{symbol}t', f'cm/{symbol}_perp']

    return all_symbols


def generate_all_timeframe_regular():
    return [lti.Timeframe.t1h, lti.Timeframe.t2h, lti.Timeframe.t1m, \
            lti.Timeframe.t5m, lti.Timeframe.t4h, \
            lti.Timeframe.t6h, lti.Timeframe.t12h, lti.Timeframe.t8h, \
            lti.Timeframe.t15m, lti.Timeframe.t30m, lti.Timeframe.t1d]


def pytest_generate_tests(metafunc):

    if 'all_symbols' in metafunc.fixturenames:
        return metafunc.parametrize("all_symbols", generate_all_symbols())

    if 'a_timeframe' in metafunc.fixturenames:
        return metafunc.parametrize("a_timeframe", generate_all_timeframe_regular())

