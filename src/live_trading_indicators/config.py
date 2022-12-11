import os
from os import path
from pathlib import Path
import json
import datetime as dt
from .constants import CONFIG_FILE_NAME


def get_home_folder():
    return path.join(Path.home(), '.lti')


def config_get_default():

    home_folder = get_home_folder()

    return {
        'cache_folder': path.join(home_folder, 'data', 'timeframe_data'),
        'sources_folder': path.join(home_folder, 'data', 'sources'),
        'log_folder': path.join(home_folder, 'logs'),
        'source_type': 'online',
        'endpoints_required': True,
        'max_empty_bars_fraction': 0.0,
        'max_empty_bars_consecutive': 0,
        'restore_empty_bars': True,
        'print_log': True,
        'log_level': 'INFO'
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


def get_logging_config(config):

    log_folder = config['log_folder']
    if not os.path.isdir(log_folder):
        os.makedirs(log_folder)

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s:%(name)s:%(process)d:%(lineno)d ' '%(levelname)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'logfile': {
                'class': 'logging.handlers.RotatingFileHandler',
                # 'when': 's',
                'filename': path.join(log_folder, 'live-trading-indicators.log'),
                'formatter': 'default',
                'backupCount': 5,
            },
            'verbose_output': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
        },
        'root': {'level': config['log_level'], 'handlers': ['logfile', 'verbose_output'] if config['print_log'] else ['logfile']},
    }
