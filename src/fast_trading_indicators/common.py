import datetime
import os.path as path
import datetime as dt
from pathlib import Path
from enum import IntEnum

__all__ = [

    'PRICE_TYPE',
    'VOLUME_TYPE',
    'TIME_TYPE',
    'DEFAULT_DATA_PATH',

    'Timeframe',
    'FTIException',
    'FTIExceptionBadSourceData',
    'FTIExceptionTooManyEmptyBars',
    'IndicatorData',

    'date_from_arg',

]

import numpy as np

PRICE_TYPE = float
VOLUME_TYPE = float
TIME_TYPE = 'datetime64[ms]'
DEFAULT_DATA_PATH = path.join(Path.home(), '.fti')


class Timeframe(IntEnum):
    t1m = 60
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


class FTIException(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        if self.message:
            return f'{self.__class__.__name__}: {self.message}'
        else:
            return self.__class__.__name__


class FTIExceptionBadSourceData(FTIException):

    def __init__(self, data_error_message, source=None, symbol=None, day_date=None):
        self.source = source
        self.symbol = symbol
        self.date = day_date
        self.data_error_message = data_error_message
        super().__init__(f'Bad source data (source {source}, symbol {symbol}, date {day_date.date()}')


class FTIExceptionTooManyEmptyBars(FTIException):

    def __init__(self, source_name, symbol, timeframe, date_begin, date_end, fraction, consecutive):
        self.source_name = source_name
        self.symbol = symbol
        self.timeframe = timeframe
        self.date_begin = date_begin
        self.date_end = date_end
        self.fraction = fraction
        self.consecutive = consecutive

        super().__init__(
            f'Too many empty bars: fraction {fraction}, consecutive {consecutive}. '
            f'Source {source_name}, symbol {symbol}, timeframe {timeframe}, date {date_begin.date} - {date_end}.')


class IndicatorData:

    def __init__(self, data_dict):
        assert 'time' in data_dict.keys()
        self.data = data_dict
        self.__read_only = False

    def __len__(self):
        return len(self.data.time)

    def __getitem__(self, item):

        if item == slice(None, None, None):
            return self

        if type(item.start) == dt.datetime and type(item.stop) == dt.datetime and item.step is None:
            return self.slice(item.start, item.stop)

        if type(item.start) == dt.datetime and item.stop is None and item.step is None:
            return self.slice(item.start, item.stop)

        if type(item.start) == int and type(item.stop) == int and item.step is None:
            return self.slice_by_int(item.start, item.stop)

        if type(item.start) == int and item.stop is None and item.step is None:
            return self.slice_by_int(item.start, item.stop)

        raise NotImplementedError

    def __getattr__(self, item):
        return self.data[item]

    def __deepcopy__(self, memodict={}):
        return self.copy()

    def copy(self):

        new_data = {}
        for key, value in self.data.items():
            if type(value) == np.ndarray:
                new_data[key] = value.copy()
            else:
                new_data[key] = value

        return IndicatorData(new_data)

    def index_from_time(self, time):
        if time is None: return None
        return int((time - self.date_begin).total_seconds() / self.timeframe.value)

    def slice(self, time_start, time_stop):

        i_start = self.index_from_time(time_start)
        i_stop = self.index_from_time(time_stop)

        return self.slice_by_int(i_start, i_stop)

    def slice_by_int(self, i_start, i_stop):

        new_data = {}
        for key, value in self.data.items():
            if type(value) == np.ndarray:
                new_data[key] = value[i_start : i_stop]
            else:
                new_data[key] = value

        new_data['date_begin'] = self.time[i_start]
        new_data['date_end'] = self.time[i_stop - 1 if i_stop else -1]
        new_indicator_data = IndicatorData(new_data)
        if self.read_only:
            new_indicator_data.read_only = True

        return new_indicator_data

    def __eq__(self, other):

        for key, value in self.data.items():
            if type(value) == np.ndarray:
                if (other.data[key] != value).any():
                    return False
            else:
                if other.data[key] != value:
                    return False

        return True

    def __read_only_set(self, flag_value):

        if self.__read_only == flag_value: return

        for key, data_value in self.data.items():
            if type(data_value) == np.ndarray:
                data_value.setflags(write=not flag_value)

        self.__read_only = flag_value

    def __read_only_get(self):
        return self.__read_only

    read_only = property(__read_only_get, __read_only_set)


def date_from_arg(date_value):

    if date_value is None:
        return None

    if type(date_value) == int:
        return datetime.datetime(date_value // 10000, date_value % 10000 // 100, date_value % 100)

    assert type(date_value) == datetime.datetime
    return date_value
