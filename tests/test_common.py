import pytest
import numpy
from src.live_trading_indicators import Timeframe, help
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_SECOND
from src.live_trading_indicators.exceptions import *
import src.live_trading_indicators as lti
from src.live_trading_indicators import IndicatorData


def test_timeframe_cast():

    assert Timeframe.cast('1h') == Timeframe.cast(60 * 60 * TIME_UNITS_IN_ONE_SECOND)

    with pytest.raises(LTIExceptionBadTimeframeValue):
        t = Timeframe.cast(None)


def test_help():
    print(help(2))


def test_list():
    indicators_list = lti.indicators_list()
    assert 'ADL' in indicators_list
    assert 'RSI' in indicators_list
    assert 'VWMA' in indicators_list


def test_custom_indicator(config_default):

    symbol = 'um/ethusdt'
    timeframe = '1h'

    indicators = lti.Indicators('binance', 20220701, 20220703, custom_indicators='')
    ohlcv = indicators.OHLCV(symbol, timeframe)
    custom_inticator = indicators.test_common(symbol, timeframe)
    assert (custom_inticator.test == ohlcv.close * 2).all()


def get_indicator_out(indicators, symbol, timeframe, out_for_grow):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    return IndicatorData({
        'indicators': indicators,
        'parameters': {},
        'name': 'test',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'test': ohlcv.close * 2,
        'allowed_nan': False
    })

