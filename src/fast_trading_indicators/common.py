import datetime
import os.path as path
from enum import IntEnum

__all__ = [

    'PRICE_TYPE',
    'MAIN_DATA_PATH',
    'TIMEFRAME_DATA_PATH',
    'SOURCES_DATA_PATH',

    'Timeframe',
    'FTIException',
    'IndicatorData',

    'date_from_arg',

]

PRICE_TYPE = float
MAIN_DATA_PATH = path.join('~', '.fti')
TIMEFRAME_DATA_PATH = path.join(MAIN_DATA_PATH, 'timeframe_data')
SOURCES_DATA_PATH = path.join(MAIN_DATA_PATH, 'source_data')


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


class FTIException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'{self.__class__.__name__}: {self.message}'
        else:
            return self.__class__.__name__


class IndicatorData:

    def __init__(self, data_dict):
        assert 'time' in data_dict.keys()
        self.data = data_dict

    def __len__(self):
        return len(self.data.time)

    def __getitem__(self, item):
        assert False

    def __getattr__(self, item):
        return self.data[item]


def date_from_arg(date_value):

    if date_value is None:
        return None

    if type(date_value) == int:
        return datetime.datetime(date_value // 10000, date_value % 10000 // 100, date_value % 100)

    assert type(date_value) == datetime.datetime
    return date_value
