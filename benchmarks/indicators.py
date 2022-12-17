import timeit
import src.live_trading_indicators as lti

indicators = lti.Indicators('binance', 20210101, 20211231)
ohlcv = indicators.OHLCV('ethusdt', '1s')


time = timeit.timeit('print(indicators.MA("ethusdt", "1s", period=22))', number=1, globals={'indicators': indicators})
print(f'MA {time} seconds\n')

time = timeit.timeit('print(indicators.EMA("ethusdt", "1s", period=22))', number=1, globals={'indicators': indicators})
print(f'EMA {time} seconds\n')

time = timeit.timeit('print(indicators.Stochastic("ethusdt", "1s", period=15, period_d=22))', number=1, globals={'indicators': indicators})
print(f'Stochastic {time} seconds\n')