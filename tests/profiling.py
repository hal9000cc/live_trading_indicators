from conftest import SOURCE, SYMBOL, TIMEFRAME
from test_basic import test_different_dates
from src.fast_trading_indicators import *
from memory_profiler import profile

@profile
def memory_test():
    print('start')
    indicators = Indicators(SOURCE)
    out = indicators.OHLCV(SYMBOL, TIMEFRAME, date_begin=20220901, date_end=20220901)


memory_test()