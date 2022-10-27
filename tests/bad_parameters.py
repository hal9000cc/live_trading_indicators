import pytest
from src import live_trading_indicators as lti
from src.live_trading_indicators.exceptions import *


def test_bad_source(config_default):
    with pytest.raises(LTIExceptionBadDatasource):
        indicators = lti.Indicators('blablabla')


def test_symbol_not_found(config_default):
    with pytest.raises(LTIExceptionSymbolNotFound):
        indicators = lti.Indicators('binance', 20220702, 20220705)
        ohlcv = indicators.OHLCV('ethusd', '1h')


def test_date_begin_more_date_end(config_default):
    with pytest.raises(LTIExceptionSymbolNotFound):
        indicators = lti.Indicators('binance', 20220702, 20220701)
        ohlcv = indicators.OHLCV('ethusd', '1h')