import os
import os.path as path
import urllib
import urllib.request
import json
import numpy as np
import pandas as pd
import logging
from ..common import *
from ..datasources import ticks_2_timeframe_data

__all__ = ['datasource_name', 'init', 'DATA_URL', 'timeframe_day_data']

DATA_URL = 'https://data.binance.vision/'
SPOT_API_URL = 'https://api.binance.com/api/v3/'
UM_API_URL = 'https://fapi.binance.com/fapi/v1/'
CM_API_URL = 'https://dapi.binance.com/dapi/v1/'

source_data_path = None
symbol_set = None


def datasource_name():
    return 'binance_ticks'


def init(common_data_path=None):
    global source_data_path

    source_data_path = path.join(DEFAULT_DATA_PATH if common_data_path is None else common_data_path,
                                                                            'source_data', datasource_name())


def get_url_tick_day(symbol, date):

    symbol_parts = symbol.split('/')
    if len(symbol_parts) > 1:
        file_name = day_file_name_basic(symbol_parts[1], date, 'zip')
        url = f'data/futures/{symbol_parts[0]}/daily/trades/{symbol_parts[1].upper()}/{file_name}'
    else:
        file_name = day_file_name_basic(symbol, date, 'zip')
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


def download_tick_day_file(symbol, date, tick_day_file_name):

    logging.info(f'Download tick data for {symbol} for {date.date()}...')

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

    length = dl_file.getheader('content-length')
    buf = dl_file.read()

    file_folder = path.split(tick_day_file_name)[0]
    if not path.isdir(file_folder):
        os.makedirs(file_folder)

    with open(tick_day_file_name, 'wb') as file:
        file.write(buf)


def day_file_name_basic(symbol, date, ext):
    return f'{symbol.upper()}-trades-{date.date()}.{ext}'


def day_file_name_parts(symbol, date, ext):

    symbol_parts = symbol.split('/')

    if len(symbol_parts) > 1:
        return symbol_parts[:-1] + [day_file_name_basic(symbol_parts[-1], date, ext)]

    return [day_file_name_basic(symbol, date, ext)]


def timeframe_day_data_from_file(file_name, timeframe, date):

    trade_data = pd.read_csv(file_name, header=None)
    if trade_data[0].dtype != np.int64:
        trade_data = pd.read_csv(file_name, skiprows=1, header=None)

    time = trade_data[4].to_numpy().astype('datetime64[ms]')
    price = trade_data[1].to_numpy().astype(PRICE_TYPE)
    volume = trade_data[2].to_numpy().astype(VOLUME_TYPE)
    tick_data = IndicatorData({'time': time, 'price': price, 'volume': volume})

    return ticks_2_timeframe_data(tick_data, timeframe, date)


def timeframe_day_data(symbol, timeframe, date):

    tick_day_file_name_parts = day_file_name_parts(symbol, date, 'zip')
    tick_day_file_name = path.join(source_data_path, *tick_day_file_name_parts)

    if not path.isfile(tick_day_file_name):
        download_tick_day_file(symbol, date, tick_day_file_name)

    return timeframe_day_data_from_file(tick_day_file_name, timeframe, date)
