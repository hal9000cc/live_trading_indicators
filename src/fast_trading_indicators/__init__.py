from .common import \
    Timeframe, \
    FTIException, \
    FTIExceptionBadSourceData, \
    FTIExceptionTooManyEmptyBars, \
    IndicatorData, \
    TIME_TYPE, \
    PRICE_TYPE, \
    VOLUME_TYPE
from .indicators import Indicators


def config(actions=None, **kwargs):

    if actions == 'set_default':
        common.set_default_config()

    if len(kwargs):

        common.config |= kwargs

        for settings_name, settings_value in kwargs.items():
            if settings_value is None:
                del common.config[settings_name]

    if len(kwargs) or actions is not None:
        common.save_config()

    return common.config

