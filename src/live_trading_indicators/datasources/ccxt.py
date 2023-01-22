import numpy as np
import logging
from packaging import version
import ccxt
from ..exceptions import *
from ..constants import TIME_TYPE, TIME_TYPE_UNIT, PRICE_TYPE, VOLUME_TYPE
from ..timeframe import Timeframe
from .online_source import OnlineSource

CCXT_VERSION_REQUIRED = '2.2.92'

MAX_LIMITS = {
    'bequant': 1000,
    'bibox': 1000,
    'binance': 1000,
    'binancecoinm': 500,
    'binanceusdm': 1500
}

HISTORY_START = '2010-01-01'

if version.parse(ccxt.__version__) < version.parse(CCXT_VERSION_REQUIRED):
    raise LTIException(f'Requires a version of ccxt at least {CCXT_VERSION_REQUIRED}')


def get_source(config, datasource_id, exchange_params):
    return CCXTSource(config, datasource_id, exchange_params)


class CCXTSource(OnlineSource):

    def __init__(self, config, datasource_full_name, extra_exchange_params):

        name_patrs = datasource_full_name.split('.')

        if len(name_patrs) != 2 or name_patrs[0] != 'ccxt':
            raise LTIExceptionBadDatasource(datasource_full_name)

        self.exchange_name = name_patrs[1]
        self.exchange = getattr(ccxt, self.exchange_name)()
        self.history_start = np.datetime64(HISTORY_START)
        self.request_trys = int(config['request_trys'])

        self.limit_max = MAX_LIMITS.get(self.exchange_name, 500)
        if extra_exchange_params:
            self.limit_max = extra_exchange_params.get('limit', self.limit_max)
            self.exchange_params = {key: val for key, val in extra_exchange_params.items() if key != 'limit'}
        else:
            self.exchange_params = {}

        self.timeframes = None

        exchange_timeframes = self.exchange.timeframes
        if exchange_timeframes is not None:
            self.timeframes = set()
            for str_timeframe in exchange_timeframes:
                try:
                    timeframe = Timeframe.cast(str_timeframe)
                    self.timeframes.add(timeframe)
                except:
                    pass

    def datasource_name(self):
        return f'xxct.{self.exchange_name}'

    @staticmethod
    def get_store_names(symbol):
        return '', symbol.replace('/', '_')

    @staticmethod
    def get_timeframe_ccxt(timeframe):
        return str(timeframe)

    def bars_online_request(self, symbol, timeframe, time_start, time_end):

        if self.timeframes and timeframe not in self.timeframes:
            raise LTIExceptionBadParameterValue(f'Timeframe {timeframe!s} not support by source {self.datasource_name()}')

        ohlcv = []
        since_time = time_start
        timeframe_ccxt = self.get_timeframe_ccxt(timeframe)

        while since_time < time_end:

            since = int(since_time.astype('datetime64[ms]').astype(np.int64))
            limit = min(int((time_end - since_time).astype(np.int64) // timeframe.value + 1), self.limit_max)

            for i_try in range(self.request_trys):
                try:
                    downloaded_ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe_ccxt, since, limit, params=self.exchange_params)
                    break
                except TimeoutError as error:
                    logging.error(error)
                    if i_try >= self.request_trys - 1:
                        raise
                    logging.info('Repeat request...')

            n_bars = len(downloaded_ohlcv)
            if n_bars == 0:
                break

            logging.info(f'Download using {self.datasource_name()} symbol {symbol} timeframe {timeframe!s} from {since_time}, bars: {n_bars}')

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
