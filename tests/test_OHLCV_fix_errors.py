import pytest
import importlib
import numpy as np
import src.live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time
from src.live_trading_indicators.constants import TIME_TYPE


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', lti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_ok(config_default, test_source, symbol, timeframe, date):

    time_begin = cast_time(date)
    time_end = (np.datetime64(time_begin, 'D') + 1).astype(TIME_TYPE) - 1
    indicators = lti.Indicators(test_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

    out = lti.OHLCV_data(source_out.data).copy()
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert out == source_out


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', lti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_bad(config_default, test_source, symbol, timeframe, date):

    time_begin = cast_time(date)
    time_end = (np.datetime64(time_begin, 'D') + 1).astype(TIME_TYPE) - 1

    indicators = lti.Indicators(test_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

    out = lti.OHLCV_data(source_out.data).copy()
    out.time[0] -= np.timedelta64(1, 's')
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert out.is_empty()

    out = lti.OHLCV_data(source_out.data).copy()
    out.time[0] += np.timedelta64(1, 's')
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert out.is_empty()

    out = lti.OHLCV_data(source_out.data).copy()
    out.time[-1] -= np.timedelta64(1, 's')
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert out.is_empty()

    out = lti.OHLCV_data(source_out.data).copy()
    out.time[-1] += np.timedelta64(1, 's')
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert out.is_empty()

    out = lti.OHLCV_data(source_out.data).copy()
    out.time[3] -= np.timedelta64(1, 's')
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert out.is_empty()

    out = lti.OHLCV_data(source_out.data).copy()
    out.time[3] += np.timedelta64(1, 's')
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert out.is_empty()


@pytest.mark.parametrize('symbol, timeframe, date, skips', [
    ('um/ethusdt', lti.Timeframe.t1h, 20220901, [3]),
    ('um/ethusdt', lti.Timeframe.t1h, 20220901, [0, 5, 6]),
    ('um/ethusdt', lti.Timeframe.t1h, 20220901, [-1]),
    ('um/ethusdt', lti.Timeframe.t1h, 20220901, [0, -1]),
])
def test_bar_data_fix_skips(config_default, test_source, symbol, timeframe, date, skips):

    time_begin = cast_time(date)
    time_end = (np.datetime64(time_begin, 'D') + 1).astype(TIME_TYPE) - 1

    indicators = lti.Indicators(test_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)

    ixb = np.array([True] * len(source_out.time))
    ixb[np.array(skips)] = False
    out = lti.OHLCV_data({
        'symbol': source_out.symbol,
        'timeframe': source_out.timeframe,
        'time': source_out.time[ixb],
        'open': source_out.open[ixb],
        'high': source_out.high[ixb],
        'low': source_out.low[ixb],
        'close': source_out.close[ixb],
        'volume': source_out.volume[ixb]
    })
    out.fix_errors(time_begin.astype('datetime64[D]'))
    assert not out.is_empty()

    out.restore_bar_data()
    assert out.is_entire()


