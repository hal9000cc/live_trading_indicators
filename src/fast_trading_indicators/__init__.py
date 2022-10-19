from .exceptions import *
from .indicator_data import *
from .indicators import Indicators
from .common import Timeframe, \
                    TIME_TYPE, \
                    PRICE_TYPE, \
                    VOLUME_TYPE


def config(actions=None, **kwargs):

    if actions == 'set_default':
        config = common.config_get_default()
    else:
        config = common.config_load()

    if len(kwargs):

        config |= kwargs

        for settings_name, settings_value in kwargs.items():
            if settings_value is None:
                del config[settings_name]

    if len(kwargs) or actions is not None:
        common.config_save(config)

    return config

