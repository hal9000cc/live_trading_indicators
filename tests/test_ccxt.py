import pytest
from src import live_trading_indicators as lti


@pytest.mark.parametrize('symbol_binance, symbol_ccxt_binance, source_ccxt', [
    ('ethusdt', 'ETH/USDT', 'binance'),
    ('btcusdt', 'BTC/USDT', 'binance'),
    ('um/ethusdt', 'ETH/USDT', 'binanceusdm'),
    ('um/btcusdt', 'BTC/USDT', 'binanceusdm'),
])
def test_ccxt_binance(clear_data, a_timeframe, symbol_binance, symbol_ccxt_binance, source_ccxt):

    indicators_binance = lti.Indicators('binance', **clear_data)
    ohlcv_binance = indicators_binance.OHLCV(symbol_binance, a_timeframe, '2022-07-01', '2022-07-02')

    indicators_ccxt = lti.Indicators(f'ccxt.{source_ccxt}', **clear_data)
    ohlcv_ccxt = indicators_ccxt.OHLCV(symbol_ccxt_binance, a_timeframe, '2022-07-01', '2022-07-02')

    assert ohlcv_ccxt == ohlcv_binance


