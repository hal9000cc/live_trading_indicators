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


def compare_with_nan(value1, value2, accuracy=1e-11):

    ixb_nan1 = np.isnan(value1)
    ixb_nan2 = np.isnan(value2)

    if (ixb_nan1 != ixb_nan2).any():
        print(f'Not identical nan: {ixb_nan1.sum()}, {ixb_nan2.sum()}')
        return False

    if (~ixb_nan1).sum() == 0:
        return True

    max_error = abs(value1[~ixb_nan1] - value2[~ixb_nan1]).max()
    if max_error > accuracy:
        print(f'max error {max_error}')
        return False

    return True
