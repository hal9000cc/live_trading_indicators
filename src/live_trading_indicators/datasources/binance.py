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
        elif subsource_name == 'ticks':
            subsources_list.append(bars_of_day_from_ticks)
        else:
            raise ValueError(f'Bad value in config parameter "source_type": {source_type}')

    subsources = tuple(subsources_list)
    if not subsources:
        raise ValueError('Empty value in config parameter "source_type".')


def tickfile_name_basic(symbol, date, ext):
    assert type(date) == dt.date
    return f'{symbol.upper()}-trades-{date}.{ext}'


def barfile_name_basic(symbol, timeframe, date, ext):
    assert type(date) == dt.date
    return f'{symbol.upper()}-{timeframe}-{date}.{ext}'


def get_url_tick_day(symbol, date):

    symbol_parts = symbol.split('/')
    if len(symbol_parts) > 1:
        file_name = tickfile_name_basic(symbol_parts[1], date, 'zip')
        url = f'data/futures/{symbol_parts[0]}/daily/trades/{symbol_parts[1].upper()}/{file_name}'
    else:
        file_name = tickfile_name_basic(symbol, date, 'zip')
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


def download_ticks(symbol, date):

    download_url = get_url_tick_day(symbol, date)
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


def download_tickfile(symbol, date, tick_day_file_name):

    assert type(date) == dt.date
    logging.info(f'Download tick data for {symbol} for {date}...')

    buf = download_ticks(symbol, date)
    if buf is None: return

    file_folder = path.split(tick_day_file_name)[0]
    if not path.isdir(file_folder):
        os.makedirs(file_folder)

    temp_file_name = f'{tick_day_file_name}.tmp'
    with open(temp_file_name, 'wb') as file:
        file.write(buf)
    rename_file_force(temp_file_name, tick_day_file_name)


def read_tickfile(file_name):

    string_data_table = read_zipcsv_to_strings(file_name)

    first_line = 0 if string_data_table[0, 4].isdigit() else 1
    price = string_data_table[first_line:, 1].astype(float)
    volume = string_data_table[first_line:, 2].astype(float)
    time = string_data_table[first_line:, 4].astype(int).astype('datetime64[ms]')

    return TimeframeData({'time': time, 'price': price, 'volume': volume})


def bars_of_day_from_tickfile(file_name, symbol, timeframe, date):

    if not path.isfile(file_name):
        return OHLCV_day.empty_day(symbol, timeframe, date)

    tick_data = read_tickfile(file_name)
    return OHLCV_day.from_ticks(tick_data, symbol, timeframe, date)


def bars_of_day_from_ticks(symbol, timeframe, date):

    part, symbol_name = symbol_decode(symbol)

    file_name_tickfile = path.join(source_data_path, part, tickfile_name_basic(symbol_name, date, 'zip'))

    if not path.isfile(file_name_tickfile):
        download_tickfile(symbol, date, file_name_tickfile)

    return bars_of_day_from_tickfile(file_name_tickfile, symbol, timeframe, date)


def bars_of_day_from_klines_raw(symbol, timeframe, date):

    byte_zipcsv = download_klines(symbol, timeframe, date)
    if byte_zipcsv is None:
        return OHLCV_day.empty_day(symbol, timeframe, date)

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
    bar_data.fix_errors(date)
    return bar_data


def bars_of_day(symbol, timeframe, date):

    bar_data1 = subsources[0](symbol, timeframe, date)

    if len(subsources) < 2 or bar_data1.is_entire():
        return bar_data1

    bar_data2 = subsources[1](symbol, timeframe, date)
    bar_data1.suppliment(bar_data2)
    bar_data1.fix_errors(date)
    return bar_data1
