import pytest
import importlib
import numpy as np
import src.fast_trading_indicators as fti
from src.fast_trading_indicators.common import param_time
from src.fast_trading_indicators.datasources import binance


@pytest.mark.parametrize('symbol, timeframe, date_begin, date_end', [
    ('um/btcusdt', fti.Timeframe.t1h, 20220101, 20220131)
])
def test_bars(config_clear_data_b, default_source, symbol, timeframe, date_begin, date_end):

    indicators = fti.Indicators(default_source, date_begin=date_begin, date_end=date_end)
    out_using_ticks = indicators.OHLCV(symbol, timeframe)
    pass
