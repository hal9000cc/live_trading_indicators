import os.path as path
from enum import IntEnum

price_type = float
main_data_path = path.join('~', '.fti')
timeframe_data_path = path.join(main_data_path, 'timeframe_data')
sources_data_path = path.join(main_data_path, 'source_data')


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


class IndicatorData:

    def __init__(self, time, data_dict):
        assert 'time' in data_dict.keys()
        self.data = data_dict

    def __len__(self):
        return len(self.data.time)

    def __getitem__(self, item):
        assert False

    def __getattr__(self, item):
        return self.data[item]
