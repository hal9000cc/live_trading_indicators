import logging.config
from .exceptions import *
from .indicator_data import *
from .indicators_set import Indicators, help, indicators_list
from .timeframe import Timeframe
from .config import config_get_default, config_load, config_save
from .constants import TIME_TYPE, PRICE_TYPE, VOLUME_TYPE

__version__ = '0.6.2'


def config(actions=None, **kwargs):

    if actions == 'set_default':
        config = config_get_default()
    else:
        config = config_load()

    if len(kwargs):

        config.update(kwargs)

        for settings_name, settings_value in kwargs.items():
            if settings_value is None:
                del config[settings_name]

    if len(kwargs) or actions is not None:
        config_save(config)

    return config

