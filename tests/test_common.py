import pytest
from src.live_trading_indicators import Timeframe
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_SECOND
from src.live_trading_indicators.exceptions import *


def test_timeframe_cast():

    assert Timeframe.cast('1h') == Timeframe.cast(60 * 60 * TIME_UNITS_IN_ONE_SECOND)

    with pytest.raises(LTIExceptionBadTimeframeValue):
        t = Timeframe.cast(None)
