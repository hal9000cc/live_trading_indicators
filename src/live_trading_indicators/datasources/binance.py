import os
import os.path as path
import io
import urllib
import urllib.request
import json
import logging
import numpy as npf
from ..common import *
from ..exceptions import *
from ..indicator_data import *
from ..datasources import read_zipcsv_to_strings, rename_file_force


__all__ = ['datasource_name', 'init', 'DATA_URL', 'bars_of_day']

DATA_URL = 'https://data.binance.vision/'
SPOT_API_URL = 'https://api.binance.com/api/v3/'
UM_API_URL = 'https://fapi.binance.com/fapi/v1/'
CM_API_URL = 'https://dapi.binance.com/dapi/v1/'

DEFAULT_SYMBOL_PART = 'spot'
ONLINE_HOURS_AVAILABLE = 25

source_data_path = None
subsources = None

exchange_info_data = {}


def datasource_name():
    return __name__.split('.')[-1]


def init(config):
    global source_data_path, subsources

    source_data_path = path.join(config['sources_folder'], datasource_name())

    source_type = config['source_type']
    subsources_list = []
    for subsource_name in source_type.replace(' ', '').split(','):
        if subsource_name == 'bars':
            subsources_list.append(bars_of_day_from_klines)
        elif subsource_name == 'full_ticks':
            subsources_list.append(bars_of_day_from_full_ticks)
        elif subsource_name == 'agg_ticks':
            subsources_list.append(bars_of_day_from_agg_ticks)
        elif subsource_name == 'online':
            subsources_list.append(bars_of_day_online)
            pass
        else:
            raise ValueError(f'Bad value in config parameter "source_type": {source_type}')

    subsources = tuple(subsources_list)
    if not subsources:
        raise ValueError('Empty value in config parameter "source_type".')


def tickfile_name_basic(symbol, date, ticks_type, ext):
    assert type(date) == dt.date
    return f'{symbol.upper()}-{ticks_type}-{date}.{ext}'


def barfile_name_basic(symbol, timeframe, date, ext):
    assert type(date) == dt.date
    return f'{symbol.upper()}-{timeframe}-{date}.{ext}'


def get_url_tick_day(symbol, date, ticks_type):

    symbol_parts = symbol.split('/')
    if len(symbol_parts) > 1:
        file_name = tickfile_name_basic(symbol_parts[1], date, ticks_type, 'zip')
        url = f'data/futures/{symbol_parts[0]}/daily/{ticks_type}/{symbol_parts[1].upper()}/{file_name}'
    else:
        file_name = tickfile_name_basic(symbol, date, ticks_type, 'zip')
        url = f'data/spot/daily/trades/{symbol.upper()}/{file_name}'

    return urllib.parse.urljoin(DATA_URL, url)


def get_url_bar_day(symbol, timeframe, date):

    symbol_parts = symbol.split('/')
    if len(symbol_parts) > 1:
        file_name = barfile_name_basic(symbol_parts[1], timeframe, date, 'zip')
        url = f'data/futures/{symbol_parts[0]}/daily/klines/{symbol_parts[1].upper()}/{timeframe}/{file_name}'
    else:
        file_name = barfile_name_basic(symbol, timeframe, date, 'zip')
        url = f'data/spot/daily/klines/{symbol.upper()}/{timeframe}/{file_name}'

    return urllib.parse.urljoin(DATA_URL, url)


def symbol_decode(symbol):

    symbol_parts = symbol.lower().split('/')

    if len(symbol_parts) == 1:
        return 'spot', symbol_parts[0]

    if len(symbol_parts) == 2:
        part = symbol_parts[0]
        if part != 'um' and part != 'cm':
            raise ValueError(f'Bad symbol: {symbol}')

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


def download_file(dl_file):
    length = int(dl_file.getheader('content-length'))
    buf = dl_file.read()
    assert len(buf) == length
    return buf


def check_symbol(symbol):
    info = exchange_info(symbol)
    if info is None:
        raise LTIException(f'Symbol {symbol} not found in source {datasource_name()}.')


def download_ticks(symbol, date, ticks_type):

    download_url = get_url_tick_day(symbol, date, ticks_type)
    logging.info(f'download {download_url}...')

    try:
        dl_file = urllib.request.urlopen(download_url)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise error
        check_symbol(symbol)
        return None

    return download_file(dl_file)


def download_klines(symbol, timeframe, date):

    download_url = get_url_bar_day(symbol, timeframe, date)
    logging.info(f'download {download_url}...')

    try:
        dl_file = urllib.request.urlopen(download_url)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise error
        check_symbol(symbol)
        return None

    return download_file(dl_file)


def download_tickfile(symbol, date, ticks_type, tick_day_file_name):

    assert type(date) == dt.date
    logging.info(f'Download tick data for {symbol} for {date}...')

    buf = download_ticks(symbol, date, ticks_type)
    if buf is None:
        return

    file_folder = path.split(tick_day_file_name)[0]
    if not path.isdir(file_folder):
        os.makedirs(file_folder)

    temp_file_name = f'{tick_day_file_name}.tmp'
    with open(temp_file_name, 'wb') as file:
        file.write(buf)
    rename_file_force(temp_file_name, tick_day_file_name)


def read_tickfile(file_name, n_time_col, n_price_col, n_volume_col):

    string_data_table = read_zipcsv_to_strings(file_name)

    first_line = 0 if string_data_table[0, 4].isdigit() else 1

    price = string_data_table[first_line:, n_price_col].astype(float)
    volume = string_data_table[first_line:, n_volume_col].astype(float)
    time = string_data_table[first_line:, n_time_col].astype(int).astype('datetime64[ms]')

    return TimeframeData({'time': time, 'price': price, 'volume': volume})


def bars_of_day_from_tickfile(file_name, symbol, timeframe, date, ticks_type):

    if not path.isfile(file_name):
        return None

    if ticks_type == 'trades':
        tick_data = read_tickfile(file_name, 4, 1, 2)
    else:
        tick_data = read_tickfile(file_name, 5, 1, 2)

    return OHLCV_day.from_ticks(tick_data, symbol, timeframe, date)


def bars_of_day_from_ticks(symbol, timeframe, date, ticks_type):

    part, symbol_name = symbol_decode(symbol)

    file_name_tickfile = path.join(source_data_path, part, tickfile_name_basic(symbol_name, date, ticks_type, 'zip'))

    if not path.isfile(file_name_tickfile):
        download_tickfile(symbol, date, ticks_type, file_name_tickfile)

    return bars_of_day_from_tickfile(file_name_tickfile, symbol, timeframe, date, ticks_type)


def bars_of_day_from_agg_ticks(symbol, timeframe, date):
    return bars_of_day_from_ticks(symbol, timeframe, date, 'aggTrades')


def bars_of_day_from_full_ticks(symbol, timeframe, date):
    return bars_of_day_from_ticks(symbol, timeframe, date, 'trades')


def bars_of_day_from_klines_raw(symbol, timeframe, date):

    byte_zipcsv = download_klines(symbol, timeframe, date)
    if byte_zipcsv is None:
        return None

    string_data_table = read_zipcsv_to_strings(io.BytesIO(byte_zipcsv))
    if string_data_table is None:
        raise LTIException(f'Bad downloaded csv data: symbol {symbol}, timeframe {timeframe}, date {date}')

    first_line = 0 if string_data_table[0, 0].isdigit() else 1
    tf_open = string_data_table[first_line:, 1].astype(float)
    tf_high = string_data_table[first_line:, 2].astype(float)
    tf_low = string_data_table[first_line:, 3].astype(float)
    tf_close = string_data_table[first_line:, 4].astype(float)
    tf_volume = string_data_table[first_line:, 5].astype(float)
    tf_time = string_data_table[first_line:, 0].astype(int).astype('datetime64[ms]')

    return OHLCV_day({
        'symbol': symbol,
        'timeframe': timeframe,
        'time': tf_time,
        'open': tf_open,
        'high': tf_high,
        'low': tf_low,
        'close': tf_close,
        'volume': tf_volume})


def bars_of_day_from_klines(symbol, timeframe, date):

    bar_data = bars_of_day_from_klines_raw(symbol, timeframe, date)

    if bar_data is not None:
        bar_data.fix_errors(date)

    return bar_data


def bars_of_day_online_request(symbol, timeframe, date):
    part, symbol = symbol_decode(symbol)
    api_url = get_api_url(part)
    request_start_time = np.datetime64(date, 'ms').astype(int)
    request_end_time = ((np.datetime64(date, 'D') + 1).astype('datetime64[ms]') - 1).astype(int)
    request_limit = int(24 * 60 * 60 / timeframe.value)
    request_url = f'{api_url}klines?symbol={symbol.upper()}&interval={timeframe}&startTime={request_start_time}&endTime={request_end_time}&limit={request_limit}'
    response = urllib.request.urlopen(request_url).read()
    return json.loads(response)


def bars_of_day_online(symbol, timeframe, date):

    # online_from_time = dt.datetime.utcnow() - dt.timedelta(hours=ONLINE_HOURS_AVAILABLE)
    # if date < online_from_time.date():
    #     return None

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
        'volume': np.array(received_open, dtype=VOLUME_TYPE)
    })

    day_data.fix_errors(date)
    return day_data


def bars_of_day(symbol, timeframe, date):

    bar_data = None
    i_subsource = 0
    while True:

        bar_data_sub = subsources[i_subsource](symbol, timeframe, date)
        if bar_data is None:
            bar_data = bar_data_sub
        elif bar_data_sub is not None:
            bar_data.suppliment(bar_data_sub)

        if i_subsource == len(subsources) - 1 or (bar_data is not None and bar_data.is_entire()):
            break

        i_subsource += 1

    return OHLCV_day.empty_day(symbol, timeframe, date) if bar_data is None else bar_data
