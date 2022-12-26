import pytest
from src.live_trading_indicators import Timeframe, help
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_SECOND
from src.live_trading_indicators.exceptions import *
import src.live_trading_indicators as lti


def test_timeframe_cast():

    assert Timeframe.cast('1h') == Timeframe.cast(60 * 60 * TIME_UNITS_IN_ONE_SECOND)

    with pytest.raises(LTIExceptionBadTimeframeValue):
        t = Timeframe.cast(None)


def test_help():
    print(help())


def test_list():
    indicators_list = lti.indicators_list()
    assert 'ADL' in indicators_list
    assert 'RSI' in indicators_list
    assert 'VWMA' in indicators_list
