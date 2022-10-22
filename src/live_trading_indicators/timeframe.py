from enum import IntEnum
import numpy as np
import datetime as dt


class Timeframe(IntEnum):
    t1m = 60
    t3m = 60 * 3
    t5m = 60 * 5
    t10m = 60 * 10
    t15m = 60 * 15
    t30m = 60 * 30
    t1h = 60 * 60
    t2h = 60 * 60 * 2
    t4h = 60 * 60 * 4
    t6h = 60 * 60 * 6
    t8h = 60 * 60 * 8
    t12h = 60 * 60 * 12
    t1d = 60 * 60 * 24
    t2d = 60 * 60 * 24 * 2
    t4d = 60 * 60 * 24 * 4
    t1w = 60 * 60 * 24 * 7

    def __str__(self):
        return self.name[1:]

    def timedelta(self):
        return dt.timedelta(seconds=self.value)

    def timedelta64(self):
        return np.timedelta64(self.value, 's')

    def begin_of_tf(self, time):
        return (np.datetime64(time, 's').astype(int) // self.value * self.value).astype('datetime64[s]').astype(dt.datetime)