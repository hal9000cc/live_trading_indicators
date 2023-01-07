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


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-05')
])
def test_bad_data(config_default, test_source, a_symbol, time_begin, time_end):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, '2010-07-01', time_end, **config_default)

    with pytest.raises(LTIExceptionQuotationDataNotFound):
        ohlcv = indicators.OHLCV(a_symbol, timeframe)
