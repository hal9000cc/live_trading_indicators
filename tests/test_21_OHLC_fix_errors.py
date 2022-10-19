import pytest
import importlib
import numpy as np
import src.fast_trading_indicators as fti
from src.fast_trading_indicators.common import date_from_arg


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', fti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_ok(config_default, default_source, symbol, timeframe, date):

    use_date = date_from_arg(date)
    indicators = fti.Indicators(default_source)
    source_out = indicators.OHLCV(symbol, timeframe, date_begin=use_date, date_end=use_date)

    out = fti.OHLCV_data(source_out.data).copy()
    out.fix_errors(use_date)
    assert out == source_out


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', fti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_bad(config_default, default_source, symbol, timeframe, date):
    use_date = date_from_arg(date)
    indicators = fti.Indicators(default_source)
    source_out = indicators.OHLCV(symbol, timeframe, date_begin=use_date, date_end=use_date)

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


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', fti.Timeframe.t1h, 20220901)])
def test_bar_data_fix(config_default, default_source, symbol, timeframe, date):
    use_date = date_from_arg(date)
    indicators = fti.Indicators(default_source)
    source_out = indicators.OHLCV(symbol, timeframe, date_begin=use_date, date_end=use_date)

    out = fti.OHLCV_data({
        'symbol': source_out.symbol,
        'timeframe': source_out.timeframe
    }).copy()
    out.time[0] -= np.timedelta64(1, 's')
    out.fix_errors(use_date)
    assert out.is_empty()

