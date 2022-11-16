import logging
import urllib
import urllib.request
import json
import datetime as dt
import numpy as np
from ..constants import TIME_TYPE, TIME_TYPE_UNIT, PRICE_TYPE, VOLUME_TYPE, TIME_UNITS_IN_ONE_DAY, TIME_UNITS_IN_ONE_SECOND
from ..indicator_data import OHLCV_day
from ..exceptions import *

BINANCE_TIME_TYPE = 'datetime64[ms]'
BINANCE_TIME_TYPE_UNIT = 'ms'

SPOT_API_URL = 'https://api.binance.com/api/v3/'
UM_API_URL = 'https://fapi.binance.com/fapi/v1/'
CM_API_URL = 'https://dapi.binance.com/dapi/v1/'

DEFAULT_SYMBOL_PART = 'spot'

# Now request bar limit is 500 for spot and coin-m, and 1500 for usd-m.
# Spot and usd-m apply the restriction from the start time, but coin-m do it from the end.
# Therefore, specifying the limit for coin-m is mandatory.
REQUEST_BAR_LIMITS = {'cm': 500}

MINIMAL_BAR_LIMITS = 500

exchange_info_data = {}

request_cache = {}
REQUEST_CACHE_TIMELIFE_HOUR = 1


def datasource_name():
    return 'binance'


def init(config):
    pass


def bars_of_day(symbol, timeframe, day_date, bar_for_grow=None):

    try:

        day_data =  bars_of_day_online(symbol, timeframe, day_date, bar_for_grow)

    except urllib.error.HTTPError as error:

        if error.code not in (400,):
            raise

        info = exchange_info(symbol)
        if info is None:
            raise LTIExceptionSymbolNotFound(symbol)

        raise

    return day_data


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


def bars_of_day_online(symbol, timeframe, date, day_for_grow=None):

    assert date.dtype.name == 'datetime64[D]'
    assert day_for_grow is None \
           or (day_for_grow.time[0] == date and day_for_grow.time[-1] - day_for_grow.time[0] < TIME_UNITS_IN_ONE_DAY)

    if day_for_grow is None:
        query_time = np.datetime64(date, TIME_TYPE_UNIT)
    else:
        query_time = day_for_grow.time[-1]

    logging.info(f'Download using api symbol {symbol} timeframe {timeframe} from {query_time}...')

    received_time = []
    received_open = []
    received_high = []
    received_low = []
    received_close = []
    received_volume = []

    end_time = np.datetime64(date + 1, TIME_TYPE_UNIT)

    is_live_day = False
    while query_time < end_time:

        klines_data = bars_online_request_to_end_day(symbol, timeframe, query_time, end_time)

        if len(klines_data) == 0:
            is_live_day = True
            break

        for data_time_set in klines_data:
            received_open.append(PRICE_TYPE(data_time_set[1]))
            received_high.append(PRICE_TYPE(data_time_set[2]))
            received_low.append(PRICE_TYPE(data_time_set[3]))
            received_close.append(PRICE_TYPE(data_time_set[4]))
            received_volume.append(PRICE_TYPE(data_time_set[5]))
            received_time.append(int(data_time_set[0]))

        expected_bars = (end_time - query_time).astype(np.int64) // timeframe.value
        if len(klines_data) < expected_bars and len(klines_data) < MINIMAL_BAR_LIMITS:
            is_live_day = True
            break

        first_received_bar = np.datetime64(np.datetime64(int(klines_data[0][0]), BINANCE_TIME_TYPE_UNIT), TIME_TYPE_UNIT)
        last_received_bar = np.datetime64(np.datetime64(int(klines_data[-1][0]), BINANCE_TIME_TYPE_UNIT), TIME_TYPE_UNIT)

        assert first_received_bar == query_time

        query_time = last_received_bar + timeframe.value

    if len(received_time) == 0:
        return None

    end_index = None if is_live_day else -1

    if day_for_grow is None:
        day_data = OHLCV_day({
            'symbol': symbol,
            'timeframe': timeframe,
            'is_live_day': is_live_day,
            'time': np.array(received_time[:end_index], dtype=BINANCE_TIME_TYPE).astype(TIME_TYPE),
            'open': np.array(received_open[:end_index], dtype=PRICE_TYPE),
            'high': np.array(received_high[:end_index], dtype=PRICE_TYPE),
            'low': np.array(received_low[:end_index], dtype=PRICE_TYPE),
            'close': np.array(received_close[:end_index], dtype=PRICE_TYPE),
            'volume': np.array(received_volume[:end_index], dtype=VOLUME_TYPE)
        })
    else:
        day_data = OHLCV_day({
            'symbol': symbol,
            'timeframe': timeframe,
            'is_live_day': is_live_day,
            'time': np.hstack([day_for_grow.time[:-1], np.array(received_time[:end_index], dtype=BINANCE_TIME_TYPE).astype(TIME_TYPE)]),
            'open': np.hstack([day_for_grow.open[:-1], np.array(received_open[:end_index], dtype=PRICE_TYPE)]),
            'high': np.hstack([day_for_grow.high[:-1], np.array(received_high[:end_index], dtype=PRICE_TYPE)]),
            'low': np.hstack([day_for_grow.low[:-1], np.array(received_low[:end_index], dtype=PRICE_TYPE)]),
            'close': np.hstack([day_for_grow.close[:-1], np.array(received_close[:end_index], dtype=PRICE_TYPE)]),
            'volume': np.hstack([day_for_grow.volume[:-1], np.array(received_volume[:end_index], dtype=VOLUME_TYPE)])
        })

    day_data.fix_errors(date)

    return day_data


def bars_online_request(api_url, symbol, timeframe, start_time, end_time):

    start_time_int = start_time.astype(np.int64)
    end_time_int = end_time.astype(np.int64)

    request_url = f'{api_url}klines?symbol={symbol.upper()}&interval={timeframe}&startTime={start_time_int}&endTime={end_time_int}'

    return urllib.request.urlopen(request_url).read()


def bars_online_request_to_end_day(symbol, timeframe, start_time, end_time):

    part, symbol = symbol_decode(symbol)

    api_url = get_api_url(part)

    limit = REQUEST_BAR_LIMITS.get(part)
    if limit:
        end_time = min(end_time, start_time + timeframe.value * (limit - 1))

    response = bars_online_request(api_url, symbol, timeframe, start_time, end_time)
    return json.loads(response)


