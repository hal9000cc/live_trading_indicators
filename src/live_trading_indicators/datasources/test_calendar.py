import numpy as np
from .online_source import OnlineSource
from ..constants import TIME_TYPE, PRICE_TYPE, VOLUME_TYPE
from ..timeframe import Timeframe


def get_source(config, datasource_id, exchange_params):
    return TestCalendarSource(config, datasource_id, exchange_params)


class TestCalendarSource(OnlineSource):

    def __init__(self, config, datasource_full_name, exchange_params):
        self.config = config
        self.history_start = np.datetime64('2024-01-01')

    @staticmethod
    def datasource_name():
        return 'test_calendar'

    @staticmethod
    def get_store_names(symbol):
        return '', symbol

    def bars_online_request(self, symbol, timeframe, time_start, time_end):
        assert timeframe == Timeframe.t1d

        day_start = np.datetime64(time_start, 'D')
        day_end = np.datetime64(time_end, 'D')
        if day_end < day_start:
            return None

        time = []
        open = []
        high = []
        low = []
        close = []
        volume = []

        day = day_start
        while day <= day_end:
            ordinal = int((day - np.datetime64('2024-01-01')).astype(np.int64)) + 1
            base = float(ordinal)

            time.append(day.astype(TIME_TYPE))
            open.append(base)
            high.append(base + 10.0)
            low.append(base - 5.0)
            close.append(base + 2.0)
            volume.append(base * 100.0)
            day += 1

        if len(time) == 0:
            return None

        return (
            np.array(time, dtype=TIME_TYPE),
            np.array(open, dtype=PRICE_TYPE),
            np.array(high, dtype=PRICE_TYPE),
            np.array(low, dtype=PRICE_TYPE),
            np.array(close, dtype=PRICE_TYPE),
            np.array(volume, dtype=VOLUME_TYPE),
        )