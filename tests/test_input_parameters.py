import pytest
from src import live_trading_indicators as lti
from src.live_trading_indicators.exceptions import *
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_DAY, TIME_UNITS_IN_ONE_SECOND


@pytest.mark.parametrize('symbol', ['etcusdt', 'um/etcusdt', 'cm/ethusd_perp'])
def test_date_indicators_int(config_default, symbol, a_timeframe):

    indicators = lti.Indicators('binance', 20220701, 20220701)
    ma = indicators.MA(symbol, a_timeframe, period=1)
    assert len(ma) == TIME_UNITS_IN_ONE_DAY // a_timeframe.value


@pytest.mark.parametrize('symbol', ['etcusdt', 'um/etcusdt', 'cm/ethusd_perp'])
def test_date_indicator_int(config_default, symbol, a_timeframe):
    indicators = lti.Indicators('binance')
    ma = indicators.MA(symbol, a_timeframe, 20220701, 20220701, period=1)
    assert len(ma) == TIME_UNITS_IN_ONE_DAY // a_timeframe.value


@pytest.mark.parametrize('symbol', ['etcusdt', 'um/etcusdt', 'cm/ethusd_perp'])
def test_date_indicators_str(config_default, symbol, a_timeframe):

    indicators = lti.Indicators('binance', '2022-07-01', '2022-07-02')
    ma = indicators.MA(symbol, a_timeframe, period=1)
    assert len(ma) == TIME_UNITS_IN_ONE_DAY * 2 // a_timeframe.value


@pytest.mark.parametrize('symbol', ['etcusdt', 'um/etcusdt', 'cm/ethusd_perp'])
def test_date_indicator_str(config_default, symbol, a_timeframe):
    indicators = lti.Indicators('binance')
    ma = indicators.MA(symbol, a_timeframe, '2022-07-01', '2022-07-02', period=1)
    assert len(ma) == TIME_UNITS_IN_ONE_DAY * 2 // a_timeframe.value


@pytest.mark.parametrize('timeframe_str, minutes', [
    ('1m', 1),
    ('5m', 5),
    ('15m', 15),
    ('30m', 30),
    ('1h', 60),
    ('2h', 60 * 2),
    ('4h', 60 * 4),
    ('6h', 60 * 6),
    ('8h', 60 * 8),
    ('12h', 60 * 12),
    ('1d', 60 * 24)
])
def test_timeframe_str(config_default, timeframe_str, minutes):

    symbol = 'um/ethusdt'

    indicators = lti.Indicators('binance')
    ma = indicators.MA(symbol, timeframe_str, '2022-07-01', '2022-07-02', period=1)
    assert len(ma) == 24 * 60 * 2 // minutes

