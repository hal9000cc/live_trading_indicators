import pytest
import importlib
import numpy as np
import src.fast_trading_indicators as fti
from src.fast_trading_indicators.common import param_time


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', fti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_ok(config_default, default_source, symbol, timeframe, date):

    use_date = param_time(date, False).date()
    indicators = fti.Indicators(default_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin=use_date, time_end=use_date)

    out = fti.OHLCV_data(source_out.data).copy()
    out.fix_errors(use_date)
    assert out == source_out


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', fti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_bad(config_default, default_source, symbol, timeframe, date):
    use_date = param_time(date, False).date()
    indicators = fti.Indicators(default_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin=use_date, time_end=use_date)

    out = fti.OHLCV_data(source_out.data).copy()
    out.time[0] -= np.timedelta64(1, 's')
    out.fix_errors(use_date)
    assert out.is_empty()

    out = fti.OHLCV_data(source_out.data).copy()
    out.time[0] += np.timedelta64(1, 's')
    out.fix_errors(use_date)
    assert out.is_empty()

    out = fti.OHLCV_data(source_out.data).copy()
    out.time[-1] -= np.timedelta64(1, 's')
    out.fix_errors(use_date)
    assert out.is_empty()

    out = fti.OHLCV_data(source_out.data).copy()
    out.time[-1] += np.timedelta64(1, 's')
    out.fix_errors(use_date)
    assert out.is_empty()

    out = fti.OHLCV_data(source_out.data).copy()
    out.time[3] -= np.timedelta64(1, 's')
    out.fix_errors(use_date)
    assert out.is_empty()

    out = fti.OHLCV_data(source_out.data).copy()
    out.time[3] += np.timedelta64(1, 's')
    out.fix_errors(use_date)
    assert out.is_empty()


@pytest.mark.parametrize('symbol, timeframe, date, skips', [
    ('um/ethusdt', fti.Timeframe.t1h, 20220901, [3]),
    ('um/ethusdt', fti.Timeframe.t1h, 20220901, [0, 5, 6]),
    ('um/ethusdt', fti.Timeframe.t1h, 20220901, [-1]),
    ('um/ethusdt', fti.Timeframe.t1h, 20220901, [0, -1]),
])
def test_bar_data_fix_skips(config_default, default_source, symbol, timeframe, date, skips):
    use_date = param_time(date, False).date()
    indicators = fti.Indicators(default_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin=use_date, time_end=use_date)

    ixb = np.array([True] * len(source_out.time))
    ixb[np.array(skips)] = False
    out = fti.OHLCV_data({
        'symbol': source_out.symbol,
        'timeframe': source_out.timeframe,
        'time': source_out.time[ixb],
        'open': source_out.open[ixb],
        'high': source_out.high[ixb],
        'low': source_out.low[ixb],
        'close': source_out.close[ixb],
        'volume': source_out.volume[ixb]
    })
    out.fix_errors(use_date)
    assert not out.is_empty()

    out.restore_bar_data()
    assert out.is_entire()

