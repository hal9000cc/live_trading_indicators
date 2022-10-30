import os
from os import path
from pathlib import Path
import json
from .constants import CONFIG_FILE_NAME


def get_home_folder():
    return path.join(Path.home(), '.lti')


def config_get_default():

    home_folder = get_home_folder()

    return {
        'cash_folder': path.join(home_folder, 'data', 'timeframe_data'),
        'sources_folder': path.join(home_folder, 'data', 'sources'),
        'source_type': 'online',
        'endpoints_required': True,
        'max_empty_bars_fraction': 0.0,
        'max_empty_bars_consecutive': 0,
        'restore_empty_bars': True,
        'print_log': True
    }


def config_load():

    settings_file_name = path.join(get_home_folder(), CONFIG_FILE_NAME)

    config = config_get_default()

    if path.isfile(settings_file_name):
        with open(settings_file_name, 'r') as file:
            config |= json.load(file)

    return config


def config_save(config):

    home_folder = get_home_folder()

    if not path.isdir(home_folder):
        os.makedirs(home_folder)

    settings_file_name = path.join(home_folder, CONFIG_FILE_NAME)
    with open(settings_file_name, 'w') as file:
        json.dump(config, file)
