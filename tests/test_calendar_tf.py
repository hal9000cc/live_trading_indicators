import pytest
import numpy as np
import live_trading_indicators as lti
from common_test import *
from live_trading_indicators.cast_input_params import cast_time
from live_trading_indicators.exceptions import LTIExceptionTooLittleData
from live_trading_indicators.timeframe import Timeframe


@pytest.mark.parametrize('timeframe,date,expected', [
    (Timeframe.t1M, '2025-02-15', '2025-02-01'),
    (Timeframe.t1M, '2025-02-01', '2025-02-01'),
    (Timeframe.t3M, '2025-02-15', '2025-01-01'),
    (Timeframe.t3M, '2025-04-01', '2025-04-01'),
    (Timeframe.t1Y, '2025-08-15', '2025-01-01'),
    (Timeframe.t1Y, '2024-01-01', '2024-01-01'),
])
def test_calendar_begin_of_tf(timeframe, date, expected):
    assert timeframe.begin_of_tf(cast_time(date)) == cast_time(expected)


@pytest.mark.parametrize('tf_str,time_begin,time_end,expected_times', [
    ('1M', '2024-01-01', '2024-03-31', ['2024-01-01', '2024-02-01', '2024-03-01']),
    ('3M', '2024-01-01', '2024-06-30', ['2024-01-01', '2024-04-01']),
    ('1Y', '2024-01-01', '2025-12-31', ['2024-01-01', '2025-01-01']),
])
def test_calendar_ohlcv_aggregation_from_days(clear_data, tf_str, time_begin, time_end, expected_times):
    indicators = lti.Indicators('test_calendar', time_begin, time_end, **clear_data)
    ohlcv = indicators.OHLCV('test', tf_str)

    assert [str(item.astype('datetime64[D]')) for item in ohlcv.time] == expected_times

    for i_bar, time in enumerate(ohlcv.time):
        time_next = ohlcv.timeframe.next_bar_time(time)
        days = indicators.OHLCV('test', '1d', time, time_next - 1)
        assert len(days) > 0
        assert days.time[0] == time
        assert days.open[0] == ohlcv.open[i_bar]
        assert days.close[-1] == ohlcv.close[i_bar]
        assert days.high.max() == ohlcv.high[i_bar]
        assert days.low.min() == ohlcv.low[i_bar]
        assert days.volume.sum() == ohlcv.volume[i_bar]


def test_calendar_slice_inside_month(clear_data):
    indicators = lti.Indicators('test_calendar', '2024-01-01', '2024-05-31', **clear_data)
    ohlcv = indicators.OHLCV('test', '1M', '2024-02-10', '2024-03-20')

    assert [str(item.astype('datetime64[D]')) for item in ohlcv.time] == ['2024-02-01', '2024-03-01']


def test_calendar_slice_inside_quarter(clear_data):
    indicators = lti.Indicators('test_calendar', '2024-01-01', '2024-12-31', **clear_data)
    ohlcv = indicators.OHLCV('test', '3M', '2024-05-10', '2024-11-20')

    assert [str(item.astype('datetime64[D]')) for item in ohlcv.time] == ['2024-04-01', '2024-07-01', '2024-10-01']


def test_calendar_slice_inside_year(clear_data):
    indicators = lti.Indicators('test_calendar', '2024-01-01', '2025-12-31', **clear_data)
    ohlcv = indicators.OHLCV('test', '1Y', '2025-03-10', '2025-11-20')

    assert [str(item.astype('datetime64[D]')) for item in ohlcv.time] == ['2025-01-01']


def test_calendar_too_little_data(clear_data):
    indicators = lti.Indicators('test_calendar', '2024-02-10', '2024-02-20', **clear_data)
    with pytest.raises(LTIExceptionTooLittleData):
        indicators.OHLCV('test', '1M')


@pytest.mark.parametrize('tf_str,time_begin,time_end', [
    ('1M', '2024-01-01', '2024-06-30'),
    ('3M', '2024-01-01', '2024-12-31'),
    ('1Y', '2024-01-01', '2025-12-31'),
])
def test_calendar_volume_indicators(clear_data, tf_str, time_begin, time_end):
    indicators = lti.Indicators('test_calendar', time_begin, time_end, **clear_data)
    ohlcvm = indicators.OHLCVM('test', tf_str, timeframe_low='1d')
    clusters = indicators.VolumeClusters('test', tf_str, timeframe_low='1d')

    assert len(ohlcvm) == len(clusters)
    assert (ohlcvm.time == clusters.time).all()
    assert (ohlcvm.open == clusters.open).all()
    assert (ohlcvm.high == clusters.high).all()
    assert (ohlcvm.low == clusters.low).all()
    assert (ohlcvm.close == clusters.close).all()
    assert (ohlcvm.volume == clusters.volume).all()
    assert (ohlcvm.mv_price == clusters.mv_price).all()

    min_low_bars = min((ohlcvm.timeframe.next_bar_time(time) - time).astype(np.int64) // Timeframe.t1d.value for time in ohlcvm.time)
    expected_bins = int(min_low_bars // 5)

    assert clusters.clusters_volume.shape == (len(clusters), expected_bins)
    assert clusters.clusters_price.shape == (len(clusters), expected_bins + 1)

    for i_bar, time in enumerate(ohlcvm.time):
        time_next = ohlcvm.timeframe.next_bar_time(time)
        bars_low = indicators.OHLCV('test', '1d', time, time_next - 1)

        hist, prices = np.histogram(
            np.hstack((bars_low.high, bars_low.low, bars_low.close)),
            bins=expected_bins,
            weights=np.hstack((bars_low.volume / 3, bars_low.volume / 3, bars_low.volume / 3))
        )

        assert (hist == clusters.clusters_volume[i_bar]).all()
        assert np.allclose(prices, clusters.clusters_price[i_bar])

        i_mv = hist.argmax()
        mv_price = (prices[i_mv] + prices[i_mv + 1]) / 2
        assert mv_price == ohlcvm.mv_price[i_bar]