import numpy as np
import datetime as dt
from . import exceptions
from . import timeframe
from .constants import TIME_TYPE, TIME_TYPE_UNIT, TIME_UNITS_IN_ONE_DAY


def cast_time(time_parameter, end_of_unit=False):

    if time_parameter is None:
        return None

    if type(time_parameter) == int:
        time = np.datetime64(
            dt.datetime(time_parameter // 10000, time_parameter % 10000 // 100, time_parameter % 100), TIME_TYPE_UNIT)
        if end_of_unit:
            time += TIME_UNITS_IN_ONE_DAY - 1
        return time

    if type(time_parameter) == np.datetime64:
        if end_of_unit:
            return (time_parameter + 1).astype(TIME_TYPE) - 1
        else:
            return time_parameter.astype(TIME_TYPE)

    if type(time_parameter) == dt.date:
        if end_of_unit:
            return np.datetime64(time_parameter, TIME_TYPE_UNIT) + TIME_UNITS_IN_ONE_DAY - 1
        else:
            return np.datetime64(time_parameter, TIME_TYPE_UNIT)

    if type(time_parameter) == dt.datetime:
        return np.datetime64(time_parameter, TIME_TYPE_UNIT)

    if type(time_parameter) == str:
        return cast_time(np.datetime64(time_parameter), end_of_unit)

    raise exceptions.LTIExceptionBadTimeParameter(time_parameter)


def cast_timeframe(timeframe_value):

    tf = tf.Timeframe.cast(timeframe_value)
    if tf is None:
        raise exceptions.LTIBadTimeframeParameter(timeframe_value)

    return tf

