import numpy as np
import datetime as dt
from . import exceptions
from . import timeframe
from .constants import TIME_TYPE, TIME_TYPE_UNIT


def cast_time(time_value):
    if time_value is None:
        return None
    if type(time_value) == int:
        return np.datetime64(
            dt.datetime(time_value // 10000, time_value % 10000 // 100, time_value % 100), TIME_TYPE_UNIT)
    elif type(time_value) == np.datetime64:
        return time_value.astype(TIME_TYPE)
    elif type(time_value) == dt.date or type(time_value) == dt.datetime:
        return np.datetime64(time_value, TIME_TYPE_UNIT)
    elif type(time_value) == str:
        return np.datetime64(time_value, TIME_TYPE_UNIT)
    else:
        raise exceptions.LTIExceptionBadTimeParameter(time_value)


def cast_timeframe(timeframe_value):

    tf = tf.Timeframe.cast(timeframe_value)
    if tf is None:
        raise exceptions.LTIBadTimeframeParameter(timeframe_value)

    return tf

