import timeit
import src.live_trading_indicators as lti


def bench_test():
    indicators = lti.Indicators('binance')
    ohlcv = indicators.OHLCV('um/ethusdt', '1m', '2021-01-01', '2022-12-14')

number = 1
time = timeit.timeit('bench_test()', setup='from __main__ import bench_test', number=number) / number
print(f'{time} seconds')