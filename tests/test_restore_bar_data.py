import pytest
import importlib
import numpy as np
import src.live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time
from src.live_trading_indicators.constants import TIME_TYPE
from src.live_trading_indicators.exceptions import *


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', lti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_1(config_default, test_source, symbol, timeframe, date):
    time_begin = cast_time(date)
    time_end = time_begin
    indicators = lti.Indicators(test_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)
    assert len(source_out) == 1

    out = lti.OHLCV_data(source_out.data).copy()
    out.volume[0] = 0
    out.restore_bar_data()
    assert out.is_entire()

    out = lti.OHLCV_data(source_out.data).copy()
    out.close[0] = np.nan
    with pytest.raises(LTIExceptionQuotationDataNotFound):
        out.restore_bar_data()


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', lti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_2(config_default, test_source, symbol, timeframe, date):
    time_begin = cast_time(date)
    time_end = time_begin + timeframe.value
    indicators = lti.Indicators(test_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)
    assert len(source_out) == 2

    out = lti.OHLCV_data(source_out.data).copy()
    out.close[0] = np.nan
    out.restore_bar_data()
    assert out.is_entire()
    assert out.close[0] == out.open[1]

    out = lti.OHLCV_data(source_out.data).copy()
    out.close[1] = np.nan
    out.restore_bar_data()
    assert out.is_entire()
    assert out.close[0] == out.close[1]


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', lti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_3(config_default, test_source, symbol, timeframe, date):
    time_begin = cast_time(date)
    time_end = time_begin + timeframe.value * 2
    indicators = lti.Indicators(test_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)
    assert len(source_out) == 3

    out = lti.OHLCV_data(source_out.data).copy()
    out.close[1] = np.nan
    out.restore_bar_data()
    assert out.is_entire()
    assert out.close[1] == out.close[0]


@pytest.mark.parametrize('symbol, timeframe, date', [('um/ethusdt', lti.Timeframe.t1h, 20220901)])
def test_bar_data_fix_4(config_default, test_source, symbol, timeframe, date):
    time_begin = cast_time(date)
    time_end = time_begin + timeframe.value * 3
    indicators = lti.Indicators(test_source)
    source_out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)
    assert len(source_out) == 4

    out = lti.OHLCV_data(source_out.data).copy()
    out.close[1] = np.nan
    out.close[2] = np.nan
    out.restore_bar_data()
    assert out.is_entire()
    assert out.close[1] == out.close[0] and out.close[2] == out.close[0]

