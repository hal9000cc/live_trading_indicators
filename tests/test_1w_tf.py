import pytest
import src.live_trading_indicators
from common_test import *
import src.live_trading_indicators as lti
from src.live_trading_indicators.constants import TIME_UNITS_IN_ONE_DAY
from src.live_trading_indicators.timeframe import Timeframe
from src.live_trading_indicators.cast_input_params import cast_time
from src.live_trading_indicators.exceptions import LTIExceptionTooLittleData

@pytest.mark.parametrize('date, week_start', [
    ('2025-02-08', '2025-02-03'),
    ('2025-02-07', '2025-02-03'),
    ('2025-02-06', '2025-02-03'),
    ('2025-02-05', '2025-02-03'),
    ('2025-02-04', '2025-02-03'),
    ('2025-02-03', '2025-02-03'),
    ('2025-02-02', '2025-01-27')])
def test_timeframe(date, week_start):
    np_date = cast_time(date)
    np_week_start = cast_time(week_start)
    assert Timeframe.t1w.begin_of_tf(np_date) == np_week_start


@pytest.mark.parametrize('time_begin, time_end', [
    ('2025-02-02', '2025-02-08'),
    ('2025-01-26', '2025-02-02'),
    ('2025-01-26', '2025-02-03'),
    ('2025-01-27', '2025-02-02'),
    ('2025-01-27', '2025-02-03'),
    ('2025-01-01', '2025-02-08'),
    ('2025-01-06', '2025-02-08'),
    ('2025-02-02', '2025-02-02'),
    ('2025-01-26', '2025-02-02')
    #    ((dt.datetime.utcnow() - dt.timedelta(days=1)).date(), None, 14)  # live
])
def test_1w(config_default, test_source, test_symbol, time_begin, time_end):

    indicators = lti.Indicators(test_source, time_begin, time_end, **config_default)

    np_time_begin = cast_time(time_begin)
    np_time_end = cast_time(time_end)
    if np_time_end - np_time_begin <= TIME_UNITS_IN_ONE_DAY * 6:
        if np_time_end - np_time_begin < TIME_UNITS_IN_ONE_DAY * 6 or np_time_begin != Timeframe.t1w.begin_of_tf(np_time_begin):
            with pytest.raises(LTIExceptionTooLittleData):
                ohlcv = indicators.OHLCV(test_symbol, '1w')
            return

    ohlcv = indicators.OHLCV(test_symbol, '1w')

    for i_week_bar, time in enumerate(ohlcv.time):

        assert time.tolist().weekday() == 0

        week_days = indicators.OHLCV(test_symbol, '1d', time, time + 7 * TIME_UNITS_IN_ONE_DAY - 1)
        assert week_days.open[0] == ohlcv.open[i_week_bar]
        assert week_days.volume.sum() == ohlcv.volume[i_week_bar]
        assert week_days.high.max() == ohlcv.high[i_week_bar]
        assert week_days.low.min() == ohlcv.low[i_week_bar]

