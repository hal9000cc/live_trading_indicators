import src.live_trading_indicators as lti
import numpy as np

indicators = lti.Indicators('binance', '2022-10-29T16:00')
ohlcv = indicators.OHLCV('um/ethusdt', '1m')
pass
