import pytest
import datetime as dt
import numpy as np
import src.live_trading_indicators as lti
from src.live_trading_indicators.common import param_time


def test_check_bar_data(config_default, default_source, default_symbol, default_timeframe):

    n_bars = 10 * 24 * 60 * 60 // default_timeframe.value

    indicators = lti.Indicators(default_source, date_begin=20200101, date_end=20200110, max_empty_bars_fraction=1, max_empty_bars_consecutive=1e12)
    out = indicators.OHLCV(default_symbol, default_timeframe).copy()

    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 0 and empty_bars_consecutive == 0

    out.close[0:6] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 6

    out.close[-6:] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 12 / n_bars and empty_bars_consecutive == 6

    out = indicators.OHLCV(default_symbol, default_timeframe).copy()
    out.close[-6:] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 6

    out.close[20:32] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 18 / n_bars and empty_bars_consecutive == 12

    out.close[:6] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 24 / n_bars and empty_bars_consecutive == 12

    out = indicators.OHLCV(default_symbol, default_timeframe).copy()
    out.close[30:33] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 3 / n_bars and empty_bars_consecutive == 3

    out.close[-6:-3] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 3

    out.close[-6:] = 0
    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = out.get_skips()
    assert empty_bars_fraction == 9 / n_bars and empty_bars_consecutive == 6


def test_different_dates(config_default, default_source, default_symbol, a_timeframe):

    indicators = lti.Indicators(default_source)

    test_dates = [
        (20220901, 20220901),
        (20220901, 20220910),
        (20220902, 20220905),
        (20220825, 20220906),
        (20220801, 20220910),
        (20220801, 20220912),
        (20220710, 20220902),
        (20220801, 20220914)
    ]

    for date_begin, date_end in test_dates:
        out = indicators.OHLCV(default_symbol, a_timeframe, time_begin=date_begin, time_end=date_end)
        assert out.time[0] == np.datetime64(param_time(date_begin, False)).astype(lti.TIME_TYPE)
        assert out.time[-1] == np.datetime64(a_timeframe.begin_of_tf(param_time(date_end, True)), 'ms')

@pytest.mark.parametrize("cleared_points", [
    ([0, 1, 2, 3, 10, 11],),
    ([2],),
    ([3, 4, 5],),
    ([0],),
    ([-1],),
    ([20, 21, 22, -3, -2, -1],),
    ([0, 1, 2, 20, 21, 22, -3, -2, -1],),
])
def test_restore_bar_data(config_default, default_source, default_symbol, cleared_points):

    indicators = lti.Indicators(default_source, date_begin=20200101, date_end=20200110, max_empty_bars_fraction=1, max_empty_bars_consecutive=1000)
    out = indicators.OHLCV(default_symbol, lti.Timeframe.t1h).copy()

    for value_name in ('open', 'high', 'low', 'close', 'volume'):
        out.data[value_name][np.array(cleared_points)] = 0

    out.restore_bar_data()

    assert (out.open != 0).all()
    assert (out.high != 0).all()
    assert (out.low != 0).all()
    assert (out.close != 0).all()


def test_change_dates(config_default, default_source, default_symbol, a_timeframe):

    indicators = lti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, a_timeframe, time_begin=20220101, time_end=20220110)
    out1 = indicators.OHLCV(default_symbol, a_timeframe, time_begin=20220103, time_end=20220110)

    assert out[int(2 * 24 * 60 * 60 // a_timeframe.value):] == out1

    indicators = lti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, a_timeframe, time_begin=20220103, time_end=20220110)
    out1 = indicators.OHLCV(default_symbol, a_timeframe, time_begin=20220101, time_end=20220110)

    assert out == out1[int(2 * 24 * 60 * 60 // a_timeframe.value):]


def test_too_many_empty_bars_exception(config_default, default_source, default_symbol, default_timeframe):

    use_date_begin = param_time(20210901, False)
    use_date_end = param_time(20210901, True)
    indicators = lti.Indicators(default_source, date_begin=use_date_begin, date_end=use_date_end)
    out = indicators.OHLCV(default_symbol, default_timeframe).copy()

    empty_bars_count, empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out, default_symbol, use_date_begin, use_date_end)
    assert empty_bars_fraction == 0 and empty_bars_consecutive == 0

    test_out = out.copy()
    test_out.close[0:6] = 0
    with pytest.raises(lti.LTISourceDataNotFound) as error:
        empty_bars_count, empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(test_out, default_symbol, use_date_begin, use_date_end)

    test_out = out.copy()
    test_out.close[1:7] = 0
    with pytest.raises(lti.LTIExceptionTooManyEmptyBars) as error:
        empty_bars_count, empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(test_out, default_symbol, use_date_begin, use_date_end)


def test_indicator_not_found(config_default, default_source, default_symbol, default_timeframe):
    indicators = lti.Indicators(default_source, date_begin=20200101, date_end=20200110)
    with pytest.raises(lti.LTIExceptionIndicatorNotFound) as error:
        out = indicators.ABCD(default_symbol, default_timeframe)
