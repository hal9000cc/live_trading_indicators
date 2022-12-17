import timeit
import src.live_trading_indicators as lti


def bench_test():
    indicators = lti.Indicators('binance')
    ohlcv = indicators.OHLCV('ethusdt', '1s', 20210101, 20211231)
    print(ohlcv)

number = 1
time = timeit.timeit('bench_test()', setup='from __main__ import bench_test', number=number) / number
print(f'{time} seconds')
