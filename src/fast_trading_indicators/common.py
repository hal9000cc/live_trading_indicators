import datetime
import json
import os
import os.path as path
from pathlib import Path
import numpy as np
import datetime as dt


__all__ = [

    'PRICE_TYPE',
    'VOLUME_TYPE',
    'VOLUME_TYPE_PRECISION',
    'TIME_TYPE',
    'HOME_FOLDER',

    'param_time',
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


def param_time(time_value, as_end):

    if time_value is None:
        return None

    if type(time_value) == int:
        return datetime.datetime(time_value // 10000, time_value % 10000 // 100, time_value % 100)
    elif type(time_value) == np.datetime64:
        return time_value.astype(dt.datetime)
    elif type(time_value) == dt.date:
        if as_end:
            next_date = time_value + dt.timedelta(days=1)
            return dt.datetime(next_date.year, next_date.month, next_date.day) - dt.timedelta(microseconds=1)
        else:
            return dt.datetime(time_value.year, time_value.month, time_value.day)

    assert type(time_value) == datetime.datetime
    return time_value


def config_get_default():

    return {
        'cash_folder': path.join(HOME_FOLDER, 'data', 'timeframe_data'),
        'sources_folder': path.join(HOME_FOLDER, 'data', 'sources'),
        'source_type': 'bars, ticks',
        'endpoints_required': True,
        'max_empty_bars_fraction': 0.01,
        'max_empty_bars_consecutive': 2,
        'restore_empty_bars': True,
        'print_log': True
    }


def config_load():

    settings_file_name = path.join(HOME_FOLDER, CONFIG_FILE_NAME)

    config = config_get_default()

    if path.isfile(settings_file_name):
        with open(settings_file_name, 'r') as file:
            config |= json.load(file)

    return config


def config_save(config):

    if not path.isdir(HOME_FOLDER):
        os.makedirs(HOME_FOLDER)

    settings_file_name = path.join(HOME_FOLDER, CONFIG_FILE_NAME)
    with open(settings_file_name, 'w') as file:
        json.dump(config, file)


