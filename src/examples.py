import src.live_trading_indicators as lti
import numpy as np

indicators = lti.Indicators('binance')

print(1)
ohlcv = indicators.OHLCV('um/ethusdt', lti.Timeframe.t1h, time_begin=20210201, time_end=20210202)
macd = indicators.MACD('um/ethusdt', lti.Timeframe.t1h)
print(ohlcv)
print(np.flatnonzero(ohlcv.volume == 0))

indicators = lti.Indicators('binance', print_log=True)

print(2)
ohlcv = indicators.OHLCV('um/ethusdt', lti.Timeframe.t1h, time_begin=20200101, time_end=20221019)
print(ohlcv)
print(np.flatnonzero(ohlcv.volume == 0))

print(3)
ohlcv = indicators.OHLCV('um/ethusdt', lti.Timeframe.t1m, time_begin=20210101, time_end=20210131)
df = ohlcv.pandas()
print(df.head())

#ohlcv = indicators.OHLCV('um/etcusdt', lti.Timeframe.t1h, date_begin=dt..., date_end=20221019)
#print(ohlcv)