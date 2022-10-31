import pytest
from src import live_trading_indicators as lti
from src.live_trading_indicators.exceptions import *


def test_length_not_math(config_default):

    symbol = 'um/etcusdt'
    indicators = lti.Indicators('binance')
    ohlcv = indicators.OHLCV(symbol, '1h', 20220701, 20220702)
    ema = indicators.OHLCV(symbol, '1h', 20220701, 20220701)

    with pytest.raises(LTIException) as error:
        data = ohlcv & ema

    assert str(error.value).startswith('Length of data does not match')


def test_timeframe_not_math(config_default):

    symbol = 'um/etcusdt'
    indicators = lti.Indicators('binance')
    ohlcv = indicators.OHLCV(symbol, '1h', 20220701, 20220702)
    ema = indicators.OHLCV(symbol, '1m', 20220701, 20220701)

    with pytest.raises(LTIException) as error:
        data = ohlcv & ema

    assert str(error.value).startswith('Timeframe does not match')


def test_time_series_not_math(config_default):

    symbol = 'um/etcusdt'
    indicators = lti.Indicators('binance')
    ohlcv = indicators.OHLCV(symbol, '1h', 20220701, 20220702)
    ema = indicators.OHLCV(symbol, '1h', 20220702, 20220703)

    with pytest.raises(LTIException) as error:
        data = ohlcv & ema

    assert str(error.value).startswith('Time series of data does not match')


def test_success(config_default, a_timeframe):

    symbol = 'um/etcusdt'
    indicators = lti.Indicators('binance')
    ohlcv = indicators.OHLCV(symbol, '1h', 20220701, 20220710)
    ema = indicators.EMA(symbol, '1h', 20220701, 20220710, period=3)

    data = ohlcv & ema

    assert (data.time == ohlcv.time).all()
    assert (data.time == ema.time).all()
    assert (data.open == ohlcv.open).all()
    assert (data.high == ohlcv.high).all()
    assert (data.low == ohlcv.low).all()
    assert (data.close == ohlcv.close).all()
    assert (data.volume == ohlcv.volume).all()
    assert (data.ema_close == ema.ema_close).all()