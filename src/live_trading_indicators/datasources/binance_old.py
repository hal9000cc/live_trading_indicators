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

exchange_info_data = {}
request_bar_limit = 1500

request_cache = {}
REQUEST_CACHE_TIMELIFE_HOUR = 1


def datasource_name():
    return 'binance'


def init(config):
    global request_bar_limit
    request_bar_limit = config.get('request_bar_limit', request_bar_limit)


def bars_of_day(symbol, timeframe, day_date):

    try:

        day_data =  bars_of_day_online(symbol, timeframe, day_date)

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

    if part == 'spot':
        return SPOT_API_URL
    if part == 'um':
        return UM_API_URL
    if part == 'cm':
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


def bars_of_day_online(symbol, timeframe, date):

    logging.info(f'Download using api symbol {symbol} timeframe {timeframe} date {date}...')

    received_time = []
    received_open = []
    received_high = []
    received_low = []
    received_close = []
    received_volume = []

    time_now = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT)
    time_end = timeframe.begin_of_tf(min(np.datetime64(np.datetime64(date, 'D') + 1, TIME_TYPE_UNIT) - 1, time_now))

    query_time = date

    while True:

        klines_data = bars_online_request_to_end_day(symbol, timeframe, query_time)
        if len(klines_data) == 0:
            break

        for data_time_set in klines_data:
            received_open.append(PRICE_TYPE(data_time_set[1]))
            received_high.append(PRICE_TYPE(data_time_set[2]))
            received_low.append(PRICE_TYPE(data_time_set[3]))
            received_close.append(PRICE_TYPE(data_time_set[4]))
            received_volume.append(PRICE_TYPE(data_time_set[5]))
            received_time.append(int(data_time_set[0]))

        last_received_bar = np.datetime64(np.datetime64(int(klines_data[-1][0]), BINANCE_TIME_TYPE_UNIT), TIME_TYPE_UNIT)
        if last_received_bar >= time_end:
            break

        query_time = last_received_bar + timeframe.value

    if len(received_time) == 0:
        return None

    day_data = OHLCV_day({
        'symbol': symbol,
        'timeframe': timeframe,
        'time': np.array(received_time, dtype=BINANCE_TIME_TYPE).astype(TIME_TYPE),
        'open': np.array(received_open, dtype=PRICE_TYPE),
        'high': np.array(received_high, dtype=PRICE_TYPE),
        'low': np.array(received_low, dtype=PRICE_TYPE),
        'close': np.array(received_close, dtype=PRICE_TYPE),
        'volume': np.array(received_volume, dtype=VOLUME_TYPE)
    })

    clear_request_cache()

    day_data.fix_errors(date)
    return day_data


def bars_online_request_to_end_day(symbol, timeframe, request_start_time):

    part, symbol = symbol_decode(symbol)

    api_url = get_api_url(part)

    time_end_of_day = (np.datetime64(request_start_time, 'D') + 1).astype(TIME_TYPE) - 1
    max_request_end_time = np.datetime64(request_start_time, TIME_TYPE_UNIT) + timeframe.value * request_bar_limit - 1
    request_end_time = min(time_end_of_day, max_request_end_time)

    request_limit = request_bar_limit

    request_start_time_int = np.datetime64(request_start_time, BINANCE_TIME_TYPE_UNIT).astype(int)
    request_end_time_int = request_end_time.astype(BINANCE_TIME_TYPE).astype(int)
    request_url = f'{api_url}klines?symbol={symbol.upper()}&interval={timeframe}&startTime={request_start_time_int}&endTime={request_end_time_int}&limit={request_limit}'
    #logging.info(request_url)

    response_data = request_cache.get(request_url)
    #response_data = None
    if response_data is None:
        response = urllib.request.urlopen(request_url)
        response_content_raw = response.read()
        response_content = json.loads(response_content_raw)
        if len(response_content) > 0:
            answer_end_time = np.datetime64(response_content[-1][0], BINANCE_TIME_TYPE_UNIT)
            begin_of_now_tf = timeframe.begin_of_tf(np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT))
            begin_of_now_day = timeframe.begin_of_tf(np.datetime64(dt.datetime.utcnow().date(), TIME_TYPE_UNIT))
            if begin_of_now_day < answer_end_time < begin_of_now_tf:
                request_cache[request_url] = np.datetime64(dt.datetime.now(), TIME_TYPE_UNIT), response_content_raw
    else:
        response_content = json.loads(response_data[1])

    return response_content


def clear_request_cache():

    now = np.datetime64(dt.datetime.now(), TIME_TYPE_UNIT)
    keys_for_delete = []
    for key, value in request_cache.items():
        if (now - value[0]).astype(int) / TIME_UNITS_IN_ONE_SECOND / 60 / 60 > REQUEST_CACHE_TIMELIFE_HOUR:
            keys_for_delete.append(key)

    for key in keys_for_delete:
        request_cache.pop(key)

