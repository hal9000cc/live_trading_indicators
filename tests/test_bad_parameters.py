import pytest
from src import live_trading_indicators as lti
from src.live_trading_indicators.exceptions import *


def test_bad_source(config_default):
    with pytest.raises(LTIExceptionBadDatasource):
        indicators = lti.Indicators('blablabla')


def test_symbol_not_found(config_default, test_source):
    with pytest.raises(LTIExceptionSymbolNotFound):
        indicators = lti.Indicators(test_source, 20220702, 20220705)
        ohlcv = indicators.OHLCV('ethusd', '1h')


def test_symbol_not_found_part(config_default, test_source):
    with pytest.raises(LTIExceptionSymbolNotFound):
        indicators = lti.Indicators(test_source, 20220702, 20220705)
        ohlcv = indicators.OHLCV('ut/ethusd', '1h')


def test_date_begin_later_date_end(config_default, test_source):
    with pytest.raises(LTIExceptionTimeBeginLaterTimeEnd):
        indicators = lti.Indicators(test_source, 20220702, 20220701)
        ohlcv = indicators.OHLCV('ethusd', '1h')


def test_early_date(config_default):
    with pytest.raises(LTIExceptionBadTimeParameter):
        indicators = lti.Indicators('binance', 20160702, 20170701)
        ohlcv = indicators.OHLCV('ethusd', '1h')


def test_bad_data(config_default):

    timeframe = '5m'

    config_default['endpoints_required'] = True
    indicators = lti.Indicators('binance', '2018-07-01', '2018-07-01', **config_default)

    with pytest.raises(LTIExceptionQuotationDataNotFound):
        ohlcv = indicators.OHLCV('um/ethusdt', timeframe)


def test_bad_data1(config_default):

    timeframe = '5m'

    config_default['endpoints_required'] = False
    indicators = lti.Indicators('binance', **config_default)

    with pytest.raises(LTIExceptionQuotationDataNotFound):
        ohlcv = indicators.OHLCV('um/etcusdt', timeframe, '2020-01-15', '2020-01-15')

    indicators = lti.Indicators('binance', '2020-01-15', '2020-01-15', **config_default)

    with pytest.raises(LTIExceptionQuotationDataNotFound):
        ohlcv = indicators.OHLCV('um/etcusdt', timeframe)


def test_bad_data1(config_default):

    timeframe = '5m'

    config_default['endpoints_required'] = True
    indicators = lti.Indicators('binance', **config_default)

    with pytest.raises(LTIExceptionQuotationDataNotFound):
        ohlcv = indicators.OHLCV('um/etcusdt', timeframe, '2020-01-15', '2020-01-15')

    indicators = lti.Indicators('binance', '2020-01-15', '2020-01-15', **config_default)

    with pytest.raises(LTIExceptionQuotationDataNotFound):
        ohlcv = indicators.OHLCV('um/etcusdt', timeframe)
