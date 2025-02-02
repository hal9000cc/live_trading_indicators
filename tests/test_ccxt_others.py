import pytest
import numpy as np
from src import live_trading_indicators as lti
from src.live_trading_indicators.exceptions import *


@pytest.mark.parametrize('ccxt_source, symbol, timeframe', [
    ('bybit', 'ETHUSDT', '1h'),
    ('binancecoinm', 'ETH/USD', '1h'),
    ('binanceusdm', 'ETH/USDT', '1h'),
    ('binance', 'ETH/USDT', '1h'),
#    ('ascendex', 'ETH/USDT', '1h'),
    ('bitget', 'ETH/USDT', '1h'),
    #('okx', 'ETH/USDT', '1h')
])
def test_ccxt_sources(clear_data, ccxt_source, symbol, timeframe):

    date_begin, date_end = np.datetime64('2022-07-01'), np.datetime64('2022-07-02')

    indicators = lti.Indicators(f'ccxt.{ccxt_source}', date_begin, date_end,
                                max_empty_bars_consecutive=5, max_empty_bars_fraction=0.5, **clear_data)

    ohlcv = indicators.OHLCV(symbol, timeframe)

    assert ohlcv.time[0] == date_begin


@pytest.mark.parametrize('ccxt_source, symbol, timeframe', [
    ('binancecoinm', 'ETH/USD', '1h'),
    ('binanceusdm', 'ETH/USDT', '1h'),
    ('binance', 'ETH/USDT', '1h'),
    #('ascendex', 'ETH/USDT', '1h'),
    ('bitget', 'ETH/USDT', '1h'),
])
def test_ccxt_extra_params(clear_data, ccxt_source, symbol, timeframe):

    date_begin, date_end = np.datetime64('2022-07-01'), np.datetime64('2022-07-02')

    indicators = lti.Indicators(f'ccxt.{ccxt_source}', date_begin, date_end,
                                max_empty_bars_consecutive=5, max_empty_bars_fraction=0.5,
                                exchange_params={'limit': 100},
                                **clear_data)

    ohlcv = indicators.OHLCV(symbol, timeframe)

    assert ohlcv.time[0] == date_begin


def test_two_ccxt(clear_data):

    date_begin, date_end = np.datetime64('2022-07-01'), np.datetime64('2022-07-02')

    indicators1 = lti.Indicators('ccxt.binance', date_begin, date_end, **clear_data)
    ohlcv1 = indicators1.OHLCV('BTC/USDT', '1h')

    indicators2 = lti.Indicators('ccxt.bybit', date_begin, date_end, **clear_data)
    ohlcv2 = indicators2.OHLCV('BTC/USDT', '1h')

    assert (np.abs(ohlcv1.close - ohlcv2.close).max() < 100).all()

