import pytest
import src.live_trading_indicators as lti
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_DAY


#@pytest.mark.parametrize('timeframe', [lti.Timeframe.t1h, lti.Timeframe.t1m])
def test_check_bar_data(config_default, test_source, test_symbol, a_timeframe):

    n_bars = TIME_UNITS_IN_ONE_DAY * 40 // a_timeframe.value

    indicators = lti.Indicators(test_source, 20220701, 20220809, max_empty_bars_fraction=1, max_empty_bars_consecutive=1e12)
    out = indicators.OHLCV(test_symbol, a_timeframe).copy()

    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 0 and empty_bars_consecutive == 0

    out.close[0:6] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 6

    out.close[-6:] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 12 / n_bars and empty_bars_consecutive == 6

    out = indicators.OHLCV(test_symbol, a_timeframe).copy()
    out.close[-6:] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 6

    out.close[20:32] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 18 / n_bars and empty_bars_consecutive == 12

    out.close[:6] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 24 / n_bars and empty_bars_consecutive == 12

    out = indicators.OHLCV(test_symbol, a_timeframe).copy()
    out.close[30:33] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 3 / n_bars and empty_bars_consecutive == 3

    out.close[-6:-3] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 3

    out.close[-6:] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 9 / n_bars and empty_bars_consecutive == 6
