from src.live_trading_indicators import Timeframe
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_SECOND


def test_timeframe_cast():
    assert Timeframe.cast('1h') == Timeframe.cast(60 * 60 * TIME_UNITS_IN_ONE_SECOND)
    assert Timeframe.cast(None) is None