import numpy as np
import logging
import ccxt
from ..exceptions import *
from ..constants import TIME_TYPE, TIME_TYPE_UNIT, PRICE_TYPE, VOLUME_TYPE
from ..timeframe import Timeframe

MAX_LIMITS = {
    'bequant': 1000,
    'bibox': 1000,
    'binance': 1000,
    'binancecoinm': 500,
    'binanceusdm': 1500
}

exchange = None
exchange_name = None
timeframes = None
exchange_params = None
limit_max = None


def datasource_name():
    return f'xxct.{exchange_name}'


def init(config, datasource_full_name, extra_exchange_params):
    global exchange, exchange_name, timeframes, exchange_params, limit_max

    name_patrs = datasource_full_name.split('.')

    if len(name_patrs) != 2 or name_patrs[0] != 'ccxt':
        raise LTIExceptionBadDatasource(datasource_full_name)

    exchange_name = name_patrs[1]
    exchange = getattr(ccxt, exchange_name)()

    limit_max = MAX_LIMITS.get(exchange_name, 500)
    if extra_exchange_params:
        limit_max = extra_exchange_params.get('limit', limit_max)
        exchange_params = {key: val for key, val in extra_exchange_params.items() if key != 'limit'}
    else:
        exchange_params = {}

    exchange_timeframes = exchange.timeframes
    if exchange_timeframes is not None:
        timeframes = set()
        for str_timeframe in exchange_timeframes:
            try:
                timeframe = Timeframe.cast(str_timeframe)
                timeframes.add(timeframe)
            except:
                pass


def get_store_names(symbol):
    return '', symbol.replace('/', '_')


def get_timeframe_ccxt(timeframe):
    return str(timeframe)


def bars_online_request(symbol, timeframe, time_start, time_end):

    if timeframes and timeframe not in timeframes:
        raise LTIExceptionBadParameterValue(f'Timeframe {timeframe} not support by source {datasource_name()}')

    ohlcv = []
    since_time = time_start
    timeframe_ccxt = get_timeframe_ccxt(timeframe)

    while since_time < time_end:

        since = int(since_time.astype('datetime64[ms]').astype(np.int64))
        limit = min(int((time_end - since_time).astype(np.int64) // timeframe.value + 1), limit_max)

        downloaded_ohlcv = exchange.fetch_ohlcv(symbol, timeframe_ccxt, since, limit, params=exchange_params)

        n_bars = len(downloaded_ohlcv)
        if n_bars == 0:
            break

        logging.info(f'Download using api symbol {symbol} timeframe {timeframe} from {since}, bars: {n_bars}')

        assert len(ohlcv) == 0 or ohlcv[-1][0] < downloaded_ohlcv[0][0]
        ohlcv += downloaded_ohlcv

        since_time = timeframe.begin_of_tf(np.datetime64(int(downloaded_ohlcv[-1][0]), 'ms').astype(TIME_TYPE)) + timeframe.value

    if len(ohlcv) == 0:
        bar_data = np.zeros([0, 6], dtype=np.object)
    else:
        bar_data = np.array(ohlcv, dtype=np.object)

    return np.array(bar_data[:, 0].astype(np.int64), dtype='datetime64[ms]').astype(TIME_TYPE), \
           np.array(bar_data[:, 1], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 2], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 3], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 4], dtype=PRICE_TYPE), \
           np.array(bar_data[:, 5], dtype=VOLUME_TYPE)
