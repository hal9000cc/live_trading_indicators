import datetime
import json
import os
import os.path as path
import datetime as dt
from pathlib import Path
from enum import IntEnum
import numpy as np

__all__ = [

    'PRICE_TYPE',
    'VOLUME_TYPE',
    'VOLUME_TYPE_PRECISION',
    'TIME_TYPE',
    'HOME_FOLDER',

    'Timeframe',

    'date_from_arg',
    'config_load',
    'config_save',
    'config_get_default'

]

PRICE_TYPE = float
VOLUME_TYPE = float
VOLUME_TYPE_PRECISION = 15
TIME_TYPE = 'datetime64[ms]'
HOME_FOLDER = path.join(Path.home(), '.fti')
CONFIG_FILE_NAME = 'config.json'


class Timeframe(IntEnum):
    t1m = 60
    t5m = 60 * 5
    t10m = 60 * 10
    t15m = 60 * 15
    t30m = 60 * 30
    t1h = 60 * 60
    t2h = 60 * 60 * 2
    t4h = 60 * 60 * 4
    t6h = 60 * 60 * 6
    t8h = 60 * 60 * 8
    t12h = 60 * 60 * 12
    t1d = 60 * 60 * 24
    t2d = 60 * 60 * 24 * 2
    t4d = 60 * 60 * 24 * 4
    t1w = 60 * 60 * 24 * 7

    def __str__(self):
        return self.name[1:]


def date_from_arg(date_value):

    if date_value is None:
        return None

    if type(date_value) == int:
        return datetime.datetime(date_value // 10000, date_value % 10000 // 100, date_value % 100)

    assert type(date_value) == datetime.datetime
    return date_value


def config_get_default():

    return {
        'cash_folder': path.join(HOME_FOLDER, 'data', 'timeframe_data'),
        'sources_folder': path.join(HOME_FOLDER, 'data', 'sources'),
        'source_type': 'bars, ticks',
        'endpoints_required': True,
        'max_empty_bars_fraction': 0.01,
        'max_empty_bars_consecutive': 2,
        'restore_empty_bars': True # open=high=low=close = last price
    }


def config_load():

    settings_file_name = path.join(HOME_FOLDER, CONFIG_FILE_NAME)

    if path.isfile(settings_file_name):

        with open(settings_file_name, 'r') as file:
            config = json.load(file)

    else:

        config = config_get_default()

    return config


def config_save(config):

    if not path.isdir(HOME_FOLDER):
        os.makedirs(HOME_FOLDER)

    settings_file_name = path.join(HOME_FOLDER, CONFIG_FILE_NAME)
    with open(settings_file_name, 'w') as file:
        json.dump(config, file)


