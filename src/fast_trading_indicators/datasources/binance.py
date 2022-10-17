import os
import os.path as path
import urllib
import urllib.request
import json
import logging
import numpy as np
from ..common import *
from ..datasources import ticks_2_bar


__all__ = ['datasource_name', 'init', 'DATA_URL', 'bars_of_day']

DATA_URL = 'https://data.binance.vision/'
SPOT_API_URL = 'https://api.binance.com/api/v3/'
UM_API_URL = 'https://fapi.binance.com/fapi/v1/'
CM_API_URL = 'https://dapi.binance.com/dapi/v1/'

source_data_path = None
symbol_set = None


def datasource_name():
    return __name__.split('.')[-1]


def init():
    global source_data_path

    source_data_path = path.join(config['sources_folder'], datasource_name())


def get_url_tick_day(symbol, date):

    symbol_parts = symbol.split('/')
    if len(symbol_parts) > 1:
        file_name = tickfile_name_basic(symbol_parts[1], date, 'zip')
        url = f'data/futures/{symbol_parts[0]}/daily/trades/{symbol_parts[1].upper()}/{file_name}'
    else:
        file_name = tickfile_name_basic(symbol, date, 'zip')
        url = f'data/spot/daily/trades/{symbol.upper()}/{file_name}'

    return urllib.parse.urljoin(DATA_URL, url)


def symbols():
    global symbol_set

    if symbol_set is None:

        symbols_list = []
        for part, api_url in (('', SPOT_API_URL), ('um', UM_API_URL), ('cm', CM_API_URL)):

            url_info = urllib.parse.urljoin(api_url, 'exchangeInfo')
            response = urllib.request.urlopen(url_info).read()
            symbols_part = list(map(lambda symbol: symbol['symbol'], json.loads(response)['symbols']))

            if len(part) > 0:
                symbols_list += map(lambda symbol: f'{part}/{symbol}'.lower(), symbols_part)

        symbol_set = set(symbols_list)

    return symbol_set


def download_ticks(symbol, date):

    download_url = get_url_tick_day(symbol, date)

    try:
        dl_file = urllib.request.urlopen(download_url)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise error
        if symbol.lower() in symbols():
            raise FTIException(f'Ticks not found! Symbol {symbol}, date {date.date()}.')
        else:
            raise FTIException(f'Symbol {symbol} not found in source {datasource_name()}.')

    length = int(dl_file.getheader('content-length'))
    buf = dl_file.read()
    assert len(buf) == length
    return buf


def download_bars(symbol, timeframe, date):
    pass


def download_tickfile(symbol, date, tick_day_file_name):

    logging.info(f'Download tick data for {symbol} for {date.date()}...')

    buf = download_ticks(symbol, date)

    file_folder = path.split(tick_day_file_name)[0]
    if not path.isdir(file_folder):
        os.makedirs(file_folder)

    temp_file_name = f'{tick_day_file_name}.tmp'
    with open(temp_file_name, 'wb') as file:
        file.write(buf)
    rename_file_force(temp_file_name, tick_day_file_name)


def tickfile_name_basic(symbol, date, ext):
    return f'{symbol.upper()}-trades-{date.date()}.{ext}'


def tickfile_name_parts(symbol, date, ext):

    symbol_parts = symbol.split('/')

    if len(symbol_parts) > 1:
        return symbol_parts[:-1] + [tickfile_name_basic(symbol_parts[-1], date, ext)]

    return [tickfile_name_basic(symbol, date, ext)]


def read_tickfile(file_name):

    string_data_table = read_zipcsv_to_strings(file_name)

    first_line = 0 if string_data_table[0, 4].isdigit() else 1
    price = string_data_table[first_line:, 1].astype(float)
    volume = string_data_table[first_line:, 2].astype(float)
    time = string_data_table[first_line:, 4].astype(int).astype('datetime64[ms]')

    return IndicatorData({'time': time, 'price': price, 'volume': volume})


def bars_of_day_from_tickfile(file_name, timeframe, date):
    tick_data = read_tickfile(file_name)
    return ticks_2_bar(tick_data, timeframe, date)


def bars_of_day(symbol, timeframe, date):

    file_name_tickfile_parts = tickfile_name_parts(symbol, date, 'zip')
    file_name_tickfile = path.join(source_data_path, *file_name_tickfile_parts)

    if not path.isfile(file_name_tickfile):
        download_tickfile(symbol, date, file_name_tickfile)

    return bars_of_day_from_tickfile(file_name_tickfile, timeframe, date)
