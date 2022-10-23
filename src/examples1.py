import src.live_trading_indicators as lti
import numpy as np

indicators = lti.Indicators('binance')
ohlcv = indicators.OHLCV('um/ethusdt', lti.Timeframe.t1m, time_begin=20220901, time_end=20221023)
pass
