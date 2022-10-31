import live_trading_indicators as lti
import datetime as dt

indicators = lti.Indicators('binance', dt.datetime.utcnow() - dt.timedelta(minutes=6), with_incomplete_bar=True)
ohlcv = indicators.OHLCV('btcusdt', '1m')
print(ohlcv.pandas().head())

indicators = lti.Indicators('binance')
ohlcv = indicators.OHLCV('ethusdt', '4h', '2022-07-01', '2022-07-01')
print(ohlcv)

dataframe = ohlcv.pandas()
print(dataframe.head())

macd = indicators.MACD('ethusdt', '1h', '2022-07-01', '2022-07-30', period_short=15, period_long=26, period_signal=9)
print(macd.pandas().head())

ohlcv = indicators.OHLCV('ethusdt', '1h', '2022-07-01', '2022-07-30')
macd = indicators.MACD('ethusdt', '1h', '2022-07-01', '2022-07-30', period_short=15, period_long=26, period_signal=9)
cd = ohlcv & macd
print(cd.pandas().head())

import datetime as dt
indicators = lti.Indicators('binance', dt.datetime.utcnow() - dt.timedelta(minutes=6))
ohlcv = indicators.OHLCV('btcusdt', '1m')
print(ohlcv.pandas().head())

indicators = lti.Indicators('binance', dt.datetime.utcnow() - dt.timedelta(minutes=6), with_incomplete_bar=True)
ohlcv = indicators.OHLCV('btcusdt', '1m')
print(ohlcv.pandas().head())

pass