import numpy as np
import ccxt
from ..exceptions import *
from ..constants import TIME_TYPE, TIME_TYPE_UNIT, PRICE_TYPE, VOLUME_TYPE

exchange = None
exchange_name = None


def datasource_name():
    return f'xxct.{exchange_name}'


def init(config, datasource_full_name):
    global exchange, exchange_name

    name_patrs = datasource_full_name.split('.')

    if len(name_patrs) != 2 or name_patrs[0] != 'ccxt':
        raise LTIExceptionBadDatasource(datasource_full_name)

    exchange_name = name_patrs[1]
    exchange = getattr(ccxt, exchange_name)()


def get_store_names(symbol):
    return '', symbol.replace('/', '_')


def get_timeframe_ccxt(timeframe):
    return str(timeframe)


def bars_online_request(symbol, timeframe, time_start, time_end):

    ohlcv = []
    since_time = time_start
    timeframe_ccxt = get_timeframe_ccxt(timeframe)

    while since_time < time_end:

        since = int(since_time.astype('datetime64[ms]').astype(np.int64))
        limit = (time_end - since_time).astype(np.int64) // timeframe.value + 1
        downloaded_ohlcv = exchange.fetch_ohlcv(symbol, timeframe_ccxt, since, limit)

        if len(downloaded_ohlcv) == 0:
            break

        assert len(ohlcv) == 0 or ohlcv[-1][0] < downloaded_ohlcv[0][0]
        ohlcv += downloaded_ohlcv

        since_time = timeframe.begin_of_tf(np.datetime64(downloaded_ohlcv[-1][0], 'ms').astype(TIME_TYPE)) + timeframe.value

    bar_data = np.array(ohlcv, dtype=np.object)

    return np.array(bar_data[:, 0], dtype='datetime64[ms]').astype(TIME_TYPE), \
           np.array(bar_data[:, 1], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 2], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 3], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 4], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 5], dtype=VOLUME_TYPE)
