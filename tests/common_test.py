import datetime as dt
import numpy as np
from stock_indicators import Quote


def ohlcv2quote(ohlcv):
    time = ohlcv.time.astype(dt.datetime)
    return [Quote(time[i], ohlcv.open[i], ohlcv.high[i], ohlcv.low[i], ohlcv.close[i], ohlcv.volume[i]) for i in range(len(ohlcv))]


def stocks2numpy(stocks, variable):

    res = []
    for item in stocks:
        res.append(item.__getattribute__(variable))

    return np.array(res, dtype=float)
