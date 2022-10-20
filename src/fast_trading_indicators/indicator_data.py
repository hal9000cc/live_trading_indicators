import datetime as dt
import numpy as np
import logging
from .common import *
from .exceptions import *


class IndicatorData:

    def __init__(self, data_dict):
        assert 'time' in data_dict.keys()
        self.data = data_dict
        self.__read_only = False

        self.first_bar_time = self.data['time'][0].astype(dt.datetime)
        self.end_bar_time = self.data['time'][-1].astype(dt.datetime)

    def __len__(self):
        return len(self.data['time'])

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

        return self.__class__(new_data)

    def index_from_time(self, time):
        if time is None: return None
        return int((time - self.first_bar_time).total_seconds() / self.timeframe.value)

    def slice(self, time_start, time_stop):

        i_start = self.index_from_time(time_start)
        i_stop = self.index_from_time(time_stop)

        if i_start > i_stop: raise ValueError
        if i_start < 0 or i_stop < 0: raise ValueError

        return self.slice_by_int(i_start, i_stop)

    def slice_by_int(self, i_start, i_stop):

        new_data = {}
        for key, value in self.data.items():
            if type(value) == np.ndarray:
                new_data[key] = value[i_start : i_stop]
            else:
                new_data[key] = value

        new_indicator_data = IndicatorData(new_data)
        if self.read_only:
            new_indicator_data.read_only = True

        return new_indicator_data

    def __eq__(self, other):

        for key, value in self.data.items():
            if type(value) == np.ndarray:
                if (other.data.get(key) != value).any():
                    return False
            else:
                if other.data.get(key) != value:
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


class OHLCV_data(IndicatorData):

    def __init__(self, data_dict):
        super().__init__(data_dict)
        dict_keys = data_dict.keys()
        assert 'symbol' in dict_keys and 'timeframe' in dict_keys

    def clear_day(self, date):

        n_bars = 24 * 60 * 60 // self.timeframe.value
        self.first_bar_time = np.datetime64(date.date(), 'ms')

        self.data |= {
            'time': np.array([self.first_bar_time + np.timedelta64(i, 's') * self.timeframe.value for i in range(n_bars)]),
            'open': np.zeros(n_bars, dtype=PRICE_TYPE),
            'high': np.zeros(n_bars, dtype=PRICE_TYPE),
            'low': np.zeros(n_bars, dtype=PRICE_TYPE),
            'close': np.zeros(n_bars, dtype=PRICE_TYPE),
            'volume': np.zeros(n_bars, dtype=VOLUME_TYPE)
        }

        self.end_bar_time = self.data['time'][-1]

    @staticmethod
    def empty_day(symbol, timeframe, date):
        n_bars = 24 * 60 * 60 // timeframe.value
        first_bar_time = np.datetime64(date.date(), 'ms')

        return OHLCV_data({
            'symbol': symbol,
            'timeframe': timeframe,
            'time': np.array([first_bar_time + np.timedelta64(i, 's') * timeframe.value for i in range(n_bars)]),
            'open': np.zeros(n_bars, dtype=PRICE_TYPE),
            'high': np.zeros(n_bars, dtype=PRICE_TYPE),
            'low': np.zeros(n_bars, dtype=PRICE_TYPE),
            'close': np.zeros(n_bars, dtype=PRICE_TYPE),
            'volume': np.zeros(n_bars, dtype=VOLUME_TYPE)
        })

    def fix_time(self, time_need):

        if set(self.time) - set(time_need):
            return False

        if (self.time != np.sort(self.time)).any():
            return False

        n_bars = len(time_need)
        tf_time = time_need
        tf_open = np.zeros(n_bars, dtype=PRICE_TYPE)
        tf_high = np.zeros(n_bars, dtype=PRICE_TYPE)
        tf_low = np.zeros(n_bars, dtype=PRICE_TYPE)
        tf_close = np.zeros(n_bars, dtype=PRICE_TYPE)
        tf_volume = np.zeros(n_bars, dtype=VOLUME_TYPE)

        ix_time = np.searchsorted(tf_time, self.time)
        tf_open[ix_time] = self.open
        tf_high[ix_time] = self.high
        tf_low[ix_time] = self.low
        tf_close[ix_time] = self.close
        tf_volume[ix_time] = self.volume

        self.data |= {
            'time': tf_time,
            'open': tf_open,
            'high': tf_high,
            'low': tf_low,
            'close': tf_close,
            'volume': tf_volume
        }

        return True

    def fix_errors(self, date):

        if self is None or len(self.time) == 0:
            self.clear_day(date)
            return

        first_bar_time = np.datetime64(date.date(), 'ms')
        n_bars = 24 * 60 * 60 // self.timeframe.value
        time_need = np.array([first_bar_time + np.timedelta64(i, 's') * self.timeframe.value for i in range(n_bars)])

        if (len(self.time) != len(time_need) or (self.time != time_need).any()) and not self.fix_time(time_need):
            self.clear_day(date)
            return

        bx_bad_bars = \
            (self.open < 0) | \
            (self.close < 0) | \
            (self.high < self.open) | \
            (self.high < self.close) | \
            (self.low > self.open) | \
            (self.low > self.close) | \
            (self.volume < 0)

        if bx_bad_bars.sum():
            for value_name in ('open', 'high', 'low', 'close', 'volume'):
                self.data[value_name][bx_bad_bars] = 0

        self.first_bar_time = self.data['time'][0].astype(dt.datetime)
        self.end_bar_time = self.data['time'][-1].astype(dt.datetime)

    def is_entire(self):
        return (self.close > 0).all()

    def is_empty(self):
        return (self.close == 0).all()

    def suppliment(self, bar_data2):

        ix_for_restore = self.close == 0
        self.open[ix_for_restore] = bar_data2.open[ix_for_restore]
        self.high[ix_for_restore] = bar_data2.high[ix_for_restore]
        self.low[ix_for_restore] = bar_data2.low[ix_for_restore]
        self.close[ix_for_restore] = bar_data2.close[ix_for_restore]
        self.volume[ix_for_restore] = bar_data2.volume[ix_for_restore]

    def get_skips(self):

        n_bars = len(self.time)
        if n_bars == 0: raise FTIException('Bad bar data')

        bx_empty_bars = self.close == 0
        n_empty_bars = bx_empty_bars.sum()

        empty_bars_fraction = n_empty_bars / n_bars

        ix_change = np.flatnonzero(np.diff(bx_empty_bars) != 0) + 1
        intervals = np.hstack((ix_change, n_bars)) - np.hstack((0, ix_change))

        empty_bars_cons_length = intervals[0 if bx_empty_bars[0] else 1 :: 2]
        empty_bars_consecutive = empty_bars_cons_length.max() if len(empty_bars_cons_length) > 0 else 0

        return empty_bars_fraction, empty_bars_consecutive

    def restore_bar_data(self):

        n_bars = len(self.time)
        bx_empty_bars = self.volume == 0
        ix_change = np.hstack((
            np.zeros(1, dtype=int),
            np.flatnonzero(np.diff(bx_empty_bars)) + 1,
            np.array(n_bars)
        ))

        for i, point in enumerate(ix_change[:-1]):

            if self.volume[point] > 0: continue

            if point == 0:
                price = self.open[ix_change[i + 1]]
            else:
                price = self.close[point - 1]

            point_end = ix_change[i + 1]
            self.open[point: point_end] = price
            self.high[point: point_end] = price
            self.low[point: point_end] = price
            self.close[point: point_end] = price

    @staticmethod
    def from_ticks(tick_data, symbol, timeframe, date):

        assert date.time() == dt.time()

        day_start_ms = np.datetime64(date).astype('datetime64[ms]').astype(int)
        step_ms = timeframe.value * 1000
        n_candles = 24 * 60 * 60 // timeframe.value

        tick_time, tick_price, tick_volumes = tick_data.time, tick_data.price, tick_data.volume

        if len(tick_price) == 0:
            logging.warning(f'Bad ticks file - empty day, no ticks. Symbol {symbol}, date {date.date()}')
            return None

        if (tick_time[:-1] > tick_time[1:]).any():
            logging.warning(f'Bad ticks file - empty day, no ticks. Symbol {symbol}, date {date.date()}')
            return None

        first_price = tick_price[0]

        timeframe_starts = (day_start_ms + np.arange(n_candles) * step_ms).astype('datetime64[ms]')
        ix_tf_end = np.searchsorted(tick_time, timeframe_starts)[1:]
        interval_prices = np.split(tick_price, ix_tf_end)
        interval_volumes = np.split(tick_volumes, ix_tf_end)

        tf_open, tf_high, tf_low, tf_close, tf_volume = \
            np.zeros(n_candles, dtype=PRICE_TYPE), \
            np.zeros(n_candles, dtype=PRICE_TYPE), \
            np.zeros(n_candles, dtype=PRICE_TYPE), \
            np.zeros(n_candles, dtype=PRICE_TYPE), \
            np.zeros(n_candles, dtype=VOLUME_TYPE)

        tf_time = timeframe_starts

        for i_tf in range(n_candles):

            if len(interval_prices[i_tf]) == 0: continue

            tf_open[i_tf] = interval_prices[i_tf][0]
            tf_high[i_tf] = interval_prices[i_tf].max()
            tf_low[i_tf] = interval_prices[i_tf].min()
            tf_close[i_tf] = interval_prices[i_tf][-1]
            tf_volume[i_tf] = interval_volumes[i_tf].sum()

        volume_round = VOLUME_TYPE_PRECISION - int(np.ceil(np.log(tf_volume.max()) / np.log(10)))
        return OHLCV_data({
            'symbol': symbol,
            'timeframe': timeframe,
            'time': tf_time,
            'open': tf_open,
            'high': tf_high,
            'low': tf_low,
            'close': tf_close,
            'volume': np.round(tf_volume, volume_round),
        })
