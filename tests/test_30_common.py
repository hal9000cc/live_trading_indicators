import pytest
import datetime as dt
import numpy as np
import src.fast_trading_indicators as fti
from src.fast_trading_indicators.common import date_from_arg, HOME_FOLDER


def test_check_bar_data(config_default, default_source, default_symbol, default_timeframe):

    n_bars = 10 * 24 * 60 * 60 // default_timeframe.value

    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200110, max_empty_bars_fraction=1, max_empty_bars_consecutive=1e12)
    out = indicators.OHLCV(default_symbol, default_timeframe).copy()

    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 0 and empty_bars_consecutive == 0

    out.volume[0:6] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 6

    out.volume[-6:] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 12 / n_bars and empty_bars_consecutive == 6

    out = indicators.OHLCV(default_symbol, default_timeframe).copy()
    out.volume[-6:] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 6

    out.volume[20:32] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 18 / n_bars and empty_bars_consecutive == 12

    out.volume[:6] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 24 / n_bars and empty_bars_consecutive == 12

    out = indicators.OHLCV(default_symbol, default_timeframe).copy()
    out.volume[30:33] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 3 / n_bars and empty_bars_consecutive == 3

    out.volume[-6:-3] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 6 / n_bars and empty_bars_consecutive == 3

    out.volume[-6:] = 0
    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 9 / n_bars and empty_bars_consecutive == 6


def test_different_dates(config_default, default_source, default_symbol, default_timeframe):

    indicators = fti.Indicators(default_source)

    test_dates = [
        (20220901, 20220901),
        (20220901, 20220910),
        (20220902, 20220905),
        (20220925, 20221006),
        (20220901, 20221010),
        (20220901, 20221012),
        (20220810, 20221002),
        (20220901, 20221014)
    ]

    for date_begin, date_end in test_dates:
        out = indicators.OHLCV(default_symbol, default_timeframe, date_begin=date_begin, date_end=date_end)
        assert out.time[0] == np.datetime64(date_from_arg(date_begin)).astype(fti.TIME_TYPE)
        assert out.time[-1] == np.datetime64(date_from_arg(date_end) + dt.timedelta(days=1)).astype(fti.TIME_TYPE) - default_timeframe.value * 1000

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

    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200110, max_empty_bars_fraction=1, max_empty_bars_consecutive=1000)
    out = indicators.OHLCV(default_symbol, fti.Timeframe.t1h).copy()

    for value_name in ('open', 'high', 'low', 'close', 'volume'):
        out.data[value_name][np.array(cleared_points)] = 0

    indicators.restore_bar_data(out)

    assert (out.open != 0).all()
    assert (out.high != 0).all()
    assert (out.low != 0).all()
    assert (out.close != 0).all()


def test_change_dates(config_default, default_source, default_symbol, default_timeframe):

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220101, date_end=20220110)
    out1 = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220103, date_end=20220110)

    assert out[int(2 * 24 * 60 * 60 // default_timeframe.value):] == out1

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220103, date_end=20220110)
    out1 = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220101, date_end=20220110)

    assert out == out1[int(2 * 24 * 60 * 60 // default_timeframe.value):]


def test_too_many_empty_bars_exception(config_default, default_source, default_symbol, default_timeframe):

    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200110)
    out = indicators.OHLCV(default_symbol, default_timeframe).copy()

    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 0 and empty_bars_consecutive == 0

    out.volume[0:6] = 0
    with pytest.raises(fti.FTIExceptionTooManyEmptyBars) as error:
        empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)


def test_OHLCV(config_default, default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200110)
    out = indicators.OHLCV(default_symbol, default_timeframe)