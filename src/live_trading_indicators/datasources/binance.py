import logging
import urllib
import urllib.request
import json
import numpy as np
from ..constants import TIME_TYPE, PRICE_TYPE, VOLUME_TYPE, TIME_UNITS_IN_ONE_DAY
from ..indicator_data import OHLCV_day
from ..exceptions import *


SPOT_API_URL = 'https://api.binance.com/api/v3/'
UM_API_URL = 'https://fapi.binance.com/fapi/v1/'
CM_API_URL = 'https://dapi.binance.com/dapi/v1/'

DEFAULT_SYMBOL_PART = 'spot'

exchange_info_data = {}


def datasource_name():
    return 'binance'


def init(config):
    pass


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
    elif part == 'um':
        return UM_API_URL
    elif part == 'cm':
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

    klines_data = bars_of_day_online_request(symbol, timeframe, date)
    for data_time_set in klines_data:
        received_open.append(PRICE_TYPE(data_time_set[1]))
        received_high.append(PRICE_TYPE(data_time_set[2]))
        received_low.append(PRICE_TYPE(data_time_set[3]))
        received_close.append(PRICE_TYPE(data_time_set[4]))
        received_volume.append(PRICE_TYPE(data_time_set[5]))
        received_time.append(int(data_time_set[0]))

    if len(received_time) == 0:
        return None

    day_data = OHLCV_day({
        'symbol': symbol,
        'timeframe': timeframe,
        'time': np.array(received_time, dtype=TIME_TYPE),
        'open': np.array(received_open, dtype=PRICE_TYPE),
        'high': np.array(received_high, dtype=PRICE_TYPE),
        'low': np.array(received_low, dtype=PRICE_TYPE),
        'close': np.array(received_close, dtype=PRICE_TYPE),
        'volume': np.array(received_volume, dtype=VOLUME_TYPE)
    })

    day_data.fix_errors(date)
    return day_data


def bars_of_day_online_request(symbol, timeframe, date):
    part, symbol = symbol_decode(symbol)
    api_url = get_api_url(part)
    request_start_time = np.datetime64(date, 'ms').astype(int)
    request_end_time = ((np.datetime64(date, 'D') + 1).astype('datetime64[ms]') - 1).astype(int)
    request_limit = int(TIME_UNITS_IN_ONE_DAY / timeframe.value)
    request_url = f'{api_url}klines?symbol={symbol.upper()}&interval={timeframe}&startTime={request_start_time}&endTime={request_end_time}&limit={request_limit}'
    response = urllib.request.urlopen(request_url).read()
    return json.loads(response)
