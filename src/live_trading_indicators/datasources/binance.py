import logging
import urllib
import urllib.request
import json
import datetime as dt
import numpy as np
import logging
from ..constants import TIME_TYPE, TIME_TYPE_UNIT, PRICE_TYPE, VOLUME_TYPE, TIME_UNITS_IN_ONE_DAY, TIME_UNITS_IN_ONE_SECOND
from ..indicator_data import OHLCV_day
from ..exceptions import *

BINANCE_TIME_TYPE = 'datetime64[ms]'
BINANCE_TIME_TYPE_UNIT = 'ms'

SPOT_API_URL = 'https://api.binance.com/api/v3/'
UM_API_URL = 'https://fapi.binance.com/fapi/v1/'
CM_API_URL = 'https://dapi.binance.com/dapi/v1/'


# Now request bar limit is 500 for spot and coin-m, and 1500 for usd-m.
# Spot and usd-m apply the restriction from the start time, but coin-m do it from the end.
# Therefore, specifying the limit for coin-m is mandatory.
REQUEST_BAR_LIMITS = {'cm': 500, 'um': 1500, 'spot': 1000}

MINIMAL_BAR_LIMITS = 500

exchange_info_data = {}

request_cache = {}
REQUEST_CACHE_TIMELIFE_HOUR = 1

logger = logging.getLogger(__name__.split('.')[-1])


def datasource_name():
    return 'binance'


def init(config, datasource_full_name, exchange_params):
    pass


def get_store_names(symbol):

    symbol_parts = symbol.split('/')

    if len(symbol_parts) < 2:
        return 'spot', symbol

    assert len(symbol_parts) == 2
    return symbol_parts[0], symbol_parts[1]


def symbol_decode(symbol):

    symbol_parts = symbol.lower().split('/')

    if len(symbol_parts) == 1:
        return 'spot', symbol_parts[0]

    if len(symbol_parts) == 2:
        part = symbol_parts[0]
        if part != 'um' and part != 'cm':
            raise LTIExceptionSymbolNotFound(symbol)

    return part, symbol_parts[-1]


def get_api_url(part):

    match part:
        case 'spot':
            return SPOT_API_URL
        case 'um':
            return UM_API_URL
        case 'cm':
            return CM_API_URL

    raise NotImplementedError(f'Unknown part: {part}')


def download_exchange_info_part(part):
    global exchange_info_data

    api_url = get_api_url(part)
    response = urllib.request.urlopen(f'{api_url}exchangeInfo').read()
    part_info = json.loads(response)

    part_info['symbols'] = {symbol_info['symbol'].lower(): symbol_info for symbol_info in part_info['symbols']}

    exchange_info_data[part] = part_info
    return part_info


def exchange_info(symbol):
    global exchange_info_data

    part, symbol = symbol_decode(symbol)

    part_info = exchange_info_data.get(part)
    if part_info is None:
        part_info = download_exchange_info_part(part)

    return part_info['symbols'].get(symbol)


def online_request(api_url, symbol, timeframe, start_time, end_time):

    start_time_int = start_time.astype(np.int64)
    end_time_int = end_time.astype(np.int64)

    request_url = f'{api_url}klines?symbol={symbol.upper()}&interval={timeframe}&startTime={start_time_int}&endTime={end_time_int}'

    logging.debug(f'bars request {request_url=}')
    response = urllib.request.urlopen(request_url)
    used_weight = response.headers['X-MBX-USED-WEIGHT-1M']
    response_data = response.read()
    logging.debug(f'{used_weight=}')

    return response_data


def bars_online_request(symbol, timeframe, time_start, time_end):

    try:

        bars_online = bars_raw_online_request(symbol, timeframe, time_start, time_end)

    except urllib.error.HTTPError as error:

        if error.code not in (400,):
            logger.error(f'{error=}, {error.url=}')
            raise

        info = exchange_info(symbol)
        if info is None:
            raise LTIExceptionSymbolNotFound(symbol) from error

        logger.error(f'{error=}, {error.url=}')
        raise

    return bars_online


def bars_raw_online_request(symbol, timeframe, time_start, time_end):
    assert time_start.dtype.name == TIME_TYPE
    assert time_end.dtype.name == TIME_TYPE
    assert time_start <= time_end

    part, symbol = symbol_decode(symbol)

    api_url = get_api_url(part)

    limit = REQUEST_BAR_LIMITS.get(part)

    time, open, high, low, close, volume = [], [], [], [], [], []

    query_time_start = timeframe.begin_of_tf(time_start)
    while query_time_start < time_end:

        query_limit = min(limit, (time_end - query_time_start).astype(np.int64) // timeframe.value + 2)
        query_time_end = query_time_start + query_limit * timeframe.value - 1
        raw_bars_data = online_request(api_url, symbol, timeframe, query_time_start, query_time_end)
        online_bars_data = json.loads(raw_bars_data)

        n_bars = len(online_bars_data)
        if n_bars == 0:
            break

        logging.info(f'Download using api symbol {symbol} timeframe {timeframe} from {query_time_start}, bars: {n_bars}')

        data = np.array(online_bars_data)
        time.append(data[:, 0].astype(np.int64).astype(BINANCE_TIME_TYPE).astype(TIME_TYPE))
        open.append(data[:, 1].astype(PRICE_TYPE))
        high.append(data[:, 2].astype(PRICE_TYPE))
        low.append(data[:, 3].astype(PRICE_TYPE))
        close.append(data[:, 4].astype(PRICE_TYPE))
        volume.append(data[:, 5].astype(VOLUME_TYPE))

        query_time_start = timeframe.begin_of_tf(time[-1][-1]) + timeframe.value

    if len(time) == 0:
        return None

    return np.hstack(time), \
           np.hstack(open),\
           np.hstack(high),\
           np.hstack(low),\
           np.hstack(close),\
           np.hstack(volume)

