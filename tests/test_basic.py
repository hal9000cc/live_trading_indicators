import src.fast_trading_indicators as fti
import pytest
import datetime as dt
import numpy as np
from src.fast_trading_indicators.common import date_from_arg


def test_bad_datasource():
    with pytest.raises(TypeError) as error:
        indicators = fti.Indicators(None)


def test_no_date(default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, default_timeframe)
    assert error.value.message == 'No begin_date set'


def test_no_date_end(default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source, date_begin=20200101)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, default_timeframe)
    assert error.value.message == 'No end_date set'


def test_no_date_begin(default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source, date_end=20200101)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, default_timeframe)
    assert error.value.message == 'No begin_date set'


def test_OHLCV_symbol_not_found(clear_data, default_timeframe):
    indicators = fti.Indicators('binance_ticks', date_begin=20220201, date_end=20220201, common_data_path=clear_data)
    with pytest.raises(fti.FTIException) as error:
        out = indicators.OHLCV('cm/ethusd', default_timeframe)
    assert error.value.message == 'Symbol cm/ethusd not found in source binance_ticks.'


@pytest.mark.parametrize('source, symbol, date_begin, date_end, control_values', [
    ('binance_ticks', 'um/ethusdt', 20200201, 20200201,
        ([180.14, 181.36, 184.00, 184.09], [181.73, 184.10, 184.58, 184.26], [179.41, 181.31, 182.93, 182.92],
        [181.36, 184.00, 184.10, 183.79], [19477.981, 31579.898, 30595.211, 17646.828])),
    ('binance_ticks', 'um/ethusdt', 20200201, 20200202, None),
    ('binance_ticks', 'cm/ethusd_perp', 20220201, 20220201, None),
    ('binance_ticks', 'um/ethusdt', 20220930, 20220930, None),
    ('binance_ticks', 'ethusdt', 20220930, 20220930, None),
])
def test_OHLCV_clear_data(source, symbol, date_begin, date_end, control_values, clear_data):

    indicators = fti.Indicators(source, date_begin=date_begin, date_end=date_end, common_data_path=clear_data)

    out = indicators.OHLCV(symbol, fti.Timeframe.t1h)
    if control_values:
        assert (out.open[:4] == control_values[0]).all()
        assert (out.high[:4] == control_values[1]).all()
        assert (out.low[:4] == control_values[2]).all()
        assert (out.close[:4] == control_values[3]).all()
        assert (out.volume[:4] == control_values[4]).all()


def test_OHLCV(default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200110)
    out = indicators.OHLCV(default_symbol, default_timeframe)


def test_check_bar_data(default_source, default_symbol, default_timeframe):

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


def test_too_many_empty_bars_exception(default_source, default_symbol, default_timeframe):

    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200110)
    out = indicators.OHLCV(default_symbol, default_timeframe).copy()

    empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)
    assert empty_bars_fraction == 0 and empty_bars_consecutive == 0

    out.volume[0:6] = 0
    with pytest.raises(fti.FTIExceptionTooManyEmptyBars) as error:
        empty_bars_fraction, empty_bars_consecutive = indicators.check_bar_data(out)


@pytest.mark.parametrize("cleared_points", [
    ([0, 1, 2, 3, 10, 11],),
    ([2],),
    ([3, 4, 5],),
    ([0],),
    ([-1],),
    ([20, 21, 22, -3, -2, -1],),
    ([0, 1, 2, 20, 21, 22, -3, -2, -1],),
])
def test_restore_bar_data(default_source, default_symbol, cleared_points):

    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200110, max_empty_bars_fraction=1, max_empty_bars_consecutive=1000)
    out = indicators.OHLCV(default_symbol, fti.Timeframe.t1h).copy()

    for value_name in ('open', 'high', 'low', 'close', 'volume'):
        out.data[value_name][np.array(cleared_points)] = 0

    indicators.restore_bar_data(out)

    assert (out.open != 0).all()
    assert (out.high != 0).all()
    assert (out.low != 0).all()
    assert (out.close != 0).all()


def test_change_dates(default_source, default_symbol, default_timeframe):

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220101, date_end=20220110)
    out1 = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220103, date_end=20220110)

    assert out[int(2 * 24 * 60 * 60 // default_timeframe.value):] == out1

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220103, date_end=20220110)
    out1 = indicators.OHLCV(default_symbol, default_timeframe, date_begin=20220101, date_end=20220110)

    assert out == out1[int(2 * 24 * 60 * 60 // default_timeframe.value):]


def test_different_dates(default_source, default_symbol, default_timeframe):

    indicators = fti.Indicators(default_source)

    test_dates = [
        (20220301, 20220301),
        (20220301, 20220310),
        (20220302, 20220305),
        (20220225, 20220306),
        (20220301, 20220315),
        (20220201, 20220320),
        (20220210, 20220302),
    ]

    for date_begin, date_end in test_dates:
        out = indicators.OHLCV(default_symbol, default_timeframe, date_begin=date_begin, date_end=date_end)
        assert out.time[0] == np.datetime64(date_from_arg(date_begin)).astype(fti.TIME_TYPE)
        assert out.time[-1] == np.datetime64(date_from_arg(date_end) + dt.timedelta(days=1)).astype(fti.TIME_TYPE) - default_timeframe.value * 1000

