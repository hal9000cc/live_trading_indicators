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

    elif type(time_parameter) == np.datetime64:
        if end_of_unit:
            time = (time_parameter + 1).astype(TIME_TYPE) - 1
        else:
            time = time_parameter.astype(TIME_TYPE)

    elif type(time_parameter) == dt.date:
        if end_of_unit:
            time = np.datetime64(time_parameter, TIME_TYPE_UNIT) + TIME_UNITS_IN_ONE_DAY - 1
        else:
            time = np.datetime64(time_parameter, TIME_TYPE_UNIT)

    elif type(time_parameter) == dt.datetime:
        time = np.datetime64(time_parameter, TIME_TYPE_UNIT)

    elif type(time_parameter) == str:
        time = cast_time(np.datetime64(time_parameter), end_of_unit)

    else:
        raise exceptions.LTIExceptionBadTimeParameter(time_parameter)

    if time < np.datetime64('1900-01-01') or time >= np.datetime64('2100-01-01'):
        raise exceptions.LTIExceptionBadTimeParameter(f'{time_parameter} -> {time}')

    return time


