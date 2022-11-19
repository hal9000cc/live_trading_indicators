from enum import IntEnum
import numpy as np
import datetime as dt
from .constants import TIME_TYPE, TIME_TYPE_UNIT, TIME_UNITS_IN_ONE_SECOND
from .exceptions import LTIExceptionBadTimeframeValue


class Timeframe(IntEnum):
    t1m = 60 * TIME_UNITS_IN_ONE_SECOND
    t3m = 60 * 3 * TIME_UNITS_IN_ONE_SECOND
    t5m = 60 * 5 * TIME_UNITS_IN_ONE_SECOND
    t10m = 60 * 10 * TIME_UNITS_IN_ONE_SECOND
    t15m = 60 * 15 * TIME_UNITS_IN_ONE_SECOND
    t30m = 60 * 30 * TIME_UNITS_IN_ONE_SECOND
    t1h = 60 * 60 * TIME_UNITS_IN_ONE_SECOND
    t2h = 60 * 60 * 2 * TIME_UNITS_IN_ONE_SECOND
    t4h = 60 * 60 * 4 * TIME_UNITS_IN_ONE_SECOND
    t6h = 60 * 60 * 6 * TIME_UNITS_IN_ONE_SECOND
    t8h = 60 * 60 * 8 * TIME_UNITS_IN_ONE_SECOND
    t12h = 60 * 60 * 12 * TIME_UNITS_IN_ONE_SECOND
    t1d = 60 * 60 * 24 * TIME_UNITS_IN_ONE_SECOND
    t2d = 60 * 60 * 24 * 2 * TIME_UNITS_IN_ONE_SECOND
    t4d = 60 * 60 * 24 * 4 * TIME_UNITS_IN_ONE_SECOND
    t1w = 60 * 60 * 24 * 7 * TIME_UNITS_IN_ONE_SECOND

    def __str__(self):
        return self.name[1:]

    def timedelta64(self):
        return np.timedelta64(self.value, TIME_TYPE_UNIT)

    def begin_of_tf(self, time):
        assert time is not None
        return (np.datetime64(time, TIME_TYPE_UNIT).astype(np.int64) // self.value * self.value).astype(TIME_TYPE)

    @staticmethod
    def cast(value):

        if type(value) == Timeframe:
            return value

        if type(value) == int:
            try:
                return Timeframe(value)
            except Exception as exception:
                raise LTIExceptionBadTimeframeValue(value) from exception

        if type(value) == str:
            if hasattr(Timeframe, f't{value}'):
                return Timeframe[f't{value}']

        raise LTIExceptionBadTimeframeValue(value)
