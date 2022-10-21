import fast_trading_indicators as fti
import numpy as np

indicators = fti.Indicators('binance')

print(1)
ohlcv = indicators.OHLCV('um/ethusdt', fti.Timeframe.t1h, date_begin=20210201, date_end=20210202)
print(ohlcv)
print(np.flatnonzero(ohlcv.volume == 0))

indicators = fti.Indicators('binance', print_log=True)

print(2)
ohlcv = indicators.OHLCV('um/ethusdt', fti.Timeframe.t1h, date_begin=20200101, date_end=20221019)
print(ohlcv)
print(np.flatnonzero(ohlcv.volume == 0))

print(3)
ohlcv = indicators.OHLCV('um/ethusdt', fti.Timeframe.t1m, date_begin=20210101, date_end=20210131)
df = ohlcv.pandas()
print(df.head())

#ohlcv = indicators.OHLCV('um/etcusdt', fti.Timeframe.t1h, date_begin=dt..., date_end=20221019)
#print(ohlcv)