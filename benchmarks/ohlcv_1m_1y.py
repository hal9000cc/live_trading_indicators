import live_trading_indicators as lti

indicators = lti.Indicators('binance')
ohlcv = indicators.OHLCV('um/ethusdt', '1m', 20210101, 20211231)
print(ohlcv)
