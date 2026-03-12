from enum import IntEnum
import numpy as np
import datetime as dt
from .constants import TIME_TYPE, TIME_TYPE_UNIT, TIME_UNITS_IN_ONE_SECOND, TIME_UNITS_NAME_FOR_TIMEDELTA, TIME_UNITS_IN_ONE_DAY
from .exceptions import LTIExceptionBadTimeframeValue


class Timeframe(IntEnum):
    t1Y = -3
    t3M = -2
    t1M = -1
    t1s = 1 * TIME_UNITS_IN_ONE_SECOND
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
    t1w = 60 * 60 * 24 * 7 * TIME_UNITS_IN_ONE_SECOND

    def __str__(self):
        return self.name[1:]

    @property
    def is_calendar(self):
        return self.value < 0

    @property
    def approx_value(self):
        if not self.is_calendar:
            return self.value
        if self == Timeframe.t1M:
            return 30 * TIME_UNITS_IN_ONE_DAY
        if self == Timeframe.t3M:
            return 91 * TIME_UNITS_IN_ONE_DAY
        if self == Timeframe.t1Y:
            return 365 * TIME_UNITS_IN_ONE_DAY
        raise NotImplementedError(self)

    def timedelta64(self):
        return np.timedelta64(self.approx_value, TIME_TYPE_UNIT)

    def begin_of_tf(self, time):
        assert time is not None
        if self == Timeframe.t1M:
            return np.datetime64(time, TIME_TYPE_UNIT).astype('datetime64[M]').astype(TIME_TYPE)
        if self == Timeframe.t3M:
            month_time = np.datetime64(time, TIME_TYPE_UNIT).astype('datetime64[M]')
            month_int = month_time.astype(np.int64)
            return np.datetime64(int(month_int - month_int % 3), 'M').astype(TIME_TYPE)
        if self == Timeframe.t1Y:
            return np.datetime64(time, TIME_TYPE_UNIT).astype('datetime64[Y]').astype(TIME_TYPE)
        offset = 3 * TIME_UNITS_IN_ONE_DAY if self.value == self.t1w.value else 0
        return ((np.datetime64(time, TIME_TYPE_UNIT).astype(np.int64) + offset) // self.value * self.value - offset).astype(TIME_TYPE)

    def next_bar_time(self, time):
        begin_time = self.begin_of_tf(time)
        if not self.is_calendar:
            return begin_time + self.value
        if self == Timeframe.t1M:
            return (begin_time.astype('datetime64[M]') + 1).astype(TIME_TYPE)
        if self == Timeframe.t3M:
            return (begin_time.astype('datetime64[M]') + 3).astype(TIME_TYPE)
        if self == Timeframe.t1Y:
            return (begin_time.astype('datetime64[Y]') + 1).astype(TIME_TYPE)
        raise NotImplementedError(self)

    def prev_bar_time(self, time):
        begin_time = self.begin_of_tf(time)
        if not self.is_calendar:
            return begin_time - self.value
        if self == Timeframe.t1M:
            return (begin_time.astype('datetime64[M]') - 1).astype(TIME_TYPE)
        if self == Timeframe.t3M:
            return (begin_time.astype('datetime64[M]') - 3).astype(TIME_TYPE)
        if self == Timeframe.t1Y:
            return (begin_time.astype('datetime64[Y]') - 1).astype(TIME_TYPE)
        raise NotImplementedError(self)

    def timedelta(self):
        return dt.timedelta(**{TIME_UNITS_NAME_FOR_TIMEDELTA: self.approx_value})

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
