import os
import os.path as path
import construct as cs
import zlib
import logging
from ..exceptions import *
from .sqlite_cache import Sqlite3Cache
from .bars_cache import BarsCache
from ..indicator_data import *
from ..constants import PRICE_TYPE, VOLUME_TYPE


BLOCK_FILE_EXT = 'lti'

CACHE_BLOCK_VERSION = 2

DAYS_WAIT_FOR_ENTIRE = 7
MAX_CLIENT_TIME_ERROR = TIME_UNITS_IN_ONE_SECOND * 60 * 15

BARS_FOR_INTERMEDIATE_SAVE = 10000


class SourceData:

    def __init__(self, online_source, datasource_id, config):

        self.config = config
        self.cach_folder = path.join(self.config['cache_folder'], online_source.datasource_name())
        #self.request_trys = int(self.config['request_trys'])

        self.online_source = online_source
        self.datasource_id = datasource_id

        self.count_datasource_get = 0
        self.count_datasource_bars_get = 0
        self.count_file_load = 0

        self.sql_bars_cache = Sqlite3Cache(self.config)
        self.bars_cache = BarsCache()

    def __del__(self):
        del self.bars_cache

    def filename_day_data(self, symbol, timeframe, day_date):
        assert type(day_date) == np.datetime64 and day_date.dtype.name == 'datetime64[D]'

        store_folder, symbol_store_name = self.online_source.get_store_names(symbol)
        if store_folder:
            folder = path.join(self.cach_folder, store_folder)
        else:
            folder = self.cach_folder

        filename = f'{symbol_store_name}-{timeframe!s}-{day_date}.{BLOCK_FILE_EXT}'
        return folder, filename, symbol_store_name

    def save_to_cache(self, file_name, bar_data):

        n_bars = len(bar_data.time)

        data_struct = self.get_file_data_struct(n_bars)
        buf_data = [self.build_header(bar_data),
                    data_struct.build({
                    'time': bar_data.time.astype(np.int64),
                    'open': bar_data.open,
                    'high': bar_data.high,
                    'low': bar_data.low,
                    'close': bar_data.close,
                    'volume': bar_data.volume
                })]

        file_folder = path.split(file_name)[0]
        if not path.isdir(file_folder):
            os.makedirs(file_folder)

        temp_file_name = f'{file_name}.tmp'
        with open(temp_file_name, 'wb') as file:
            file.write(self.build_signature_and_version())
            file.write(zlib.compress(b''.join(buf_data)))
        self.rename_file_force(temp_file_name, file_name)

    def save_to_cache_verified(self, symbol, timeframe, bar_data, day_date):

        now = np.datetime64(dt.datetime.now(), TIME_TYPE_UNIT)

        if bar_data.is_incomplete_day:
            return

        # if bar_data.is_empty():
        #     return

        if not bar_data.is_entire():
            if (np.datetime64(now, 'D') - day_date).astype(np.int64) < DAYS_WAIT_FOR_ENTIRE:
                return

        #assert timeframe.begin_of_tf(np.datetime64(day_date, TIME_TYPE_UNIT) + TIME_UNITS_IN_ONE_DAY) + timeframe.value + MAX_CLIENT_TIME_ERROR < now
        self.sql_bars_cache.save_day(self.datasource_id, symbol, timeframe, day_date, bar_data)

    @staticmethod
    def block_header_struct():
        return cs.Struct(
            'block_version' / cs.Int8ub,
            'n_bars' / cs.Int32ub
        )

    def load_from_blocks_cache(self, symbol, timeframe, day_date):

        folder, file_name, symbol_store_name = self.filename_day_data(symbol, timeframe, day_date)

        bar_saved_data = self.bars_cache.day_load(folder, symbol_store_name, timeframe, day_date)
        if bar_saved_data is None:
            return None

        block_header_struct = self.block_header_struct()
        block_header = block_header_struct.parse(bar_saved_data[: block_header_struct.sizeof()])

        if block_header.block_version != CACHE_BLOCK_VERSION:
            raise NotImplemented(f'Unsupported block version: {block_header.block_version}')

        n_bars = block_header.n_bars

        time_type = np.dtype('>u8')
        float_type = np.dtype('>f8')
        series_data_size = n_bars * float_type.itemsize

        point = block_header_struct.sizeof()
        time = np.frombuffer(bar_saved_data, time_type, n_bars, offset=point)

        point += n_bars * time_type.itemsize
        open = np.frombuffer(bar_saved_data, float_type, n_bars, offset=point)

        point += series_data_size
        high = np.frombuffer(bar_saved_data, float_type, n_bars, offset=point)

        point += series_data_size
        low = np.frombuffer(bar_saved_data, float_type, n_bars, offset=point)

        point += series_data_size
        close = np.frombuffer(bar_saved_data, float_type, n_bars, offset=point)

        point += series_data_size
        volume = np.frombuffer(bar_saved_data, float_type, n_bars, offset=point)

        return OHLCV_day({
            'symbol': symbol,
            'timeframe': timeframe,
            'source': self.datasource_id,
            'is_incomplete_day': False,
            'time': np.array(time, dtype=np.int64).astype(TIME_TYPE),
            'open': np.array(open, dtype=PRICE_TYPE),
            'high': np.array(high, dtype=PRICE_TYPE),
            'low': np.array(low, dtype=PRICE_TYPE),
            'close': np.array(close, dtype=PRICE_TYPE),
            'volume': np.array(volume, dtype=VOLUME_TYPE)
        })

    def bars_of_day_from_cache(self, symbol, timeframe, day_date):

        bar_data = self.sql_bars_cache.load_day(self.datasource_id, symbol, timeframe, day_date)

        if bar_data is None:
            #search old files
            bar_data = self.load_from_blocks_cache(symbol, timeframe, day_date)
            if bar_data is not None:
                self.sql_bars_cache.save_day(self.datasource_id, symbol, timeframe, day_date, bar_data)

        if bar_data is not None:
            self.count_file_load += 1

        return bar_data

    def bars_online_request_with_grow(self, symbol, timeframe, query_time_start, query_time_end, day_for_grow):

        logging.debug(f'bars_online_request_with_grow {symbol} {timeframe!s} {query_time_start} {query_time_end}')
        if day_for_grow is not None and day_for_grow.time[0] == query_time_start:
            query_time_start = day_for_grow.time[-1]
            bars_data = self.online_source.bars_online_request(symbol, timeframe, query_time_start, query_time_end)
            if bars_data is not None:
                self.count_datasource_bars_get += len(bars_data[0])
                assert day_for_grow.time[-1] == bars_data[0][0]
                bars_data = np.hstack([day_for_grow.time[:-1], bars_data[0]]), \
                            np.hstack([day_for_grow.open[:-1], bars_data[1]]), \
                            np.hstack([day_for_grow.high[:-1], bars_data[2]]), \
                            np.hstack([day_for_grow.low[:-1], bars_data[3]]), \
                            np.hstack([day_for_grow.close[:-1], bars_data[4]]), \
                            np.hstack([day_for_grow.volume[:-1], bars_data[5]])
            else:
                bars_data = day_for_grow.time, day_for_grow.open, day_for_grow.high, \
                       day_for_grow.low, day_for_grow.close, day_for_grow.volume
        else:
            bars_data = self.online_source.bars_online_request(symbol, timeframe, query_time_start, query_time_end)
            if bars_data is not None:
                self.count_datasource_bars_get += len(bars_data[0])

        return bars_data

    def download_days(self, symbol, timeframe, date_start, date_end, day_for_grow):
        assert date_start.dtype.name == 'datetime64[D]'
        assert date_end.dtype.name == 'datetime64[D]'

        now = np.datetime64(dt.datetime.utcnow(), TIME_TYPE_UNIT)
        last_bar_time_of_timeframe = timeframe.begin_of_tf(now - MAX_CLIENT_TIME_ERROR)

        query_time_start = date_start.astype(TIME_TYPE)
        query_time_end = min((date_end + 1).astype(TIME_TYPE) - 1, now + MAX_CLIENT_TIME_ERROR)

        if query_time_start > query_time_end:
            return []

        bars_data = self.bars_online_request_with_grow(symbol, timeframe, query_time_start, query_time_end, day_for_grow)

        downloaded_days = []
        day_date = date_start
        while day_date <= date_end:

            time_end_day = (day_date + 1).astype(TIME_TYPE)
            time_start_day = day_date.astype(TIME_TYPE)
            if bars_data is None:
                is_incomplete_day = day_date >= last_bar_time_of_timeframe
                day_data = OHLCV_day.empty_day(symbol, timeframe, self.datasource_id, day_date, is_incomplete_day)
            else:
                i_day_start = np.searchsorted(bars_data[0], time_start_day)
                i_day_end = np.searchsorted(bars_data[0], time_end_day)

                is_incomplete_day = i_day_end >= len(bars_data[0]) and len(bars_data[0]) > 0 and bars_data[0][-1] >= last_bar_time_of_timeframe

                if i_day_start == i_day_end:
                    day_data = OHLCV_day.empty_day(symbol, timeframe, self.datasource_id, day_date, is_incomplete_day)
                else:
                    day_data = OHLCV_day({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'source': self.datasource_id,
                        'is_incomplete_day': is_incomplete_day,
                        'time': bars_data[0][i_day_start: i_day_end],
                        'open': bars_data[1][i_day_start: i_day_end],
                        'high': bars_data[2][i_day_start: i_day_end],
                        'low': bars_data[3][i_day_start: i_day_end],
                        'close': bars_data[4][i_day_start: i_day_end],
                        'volume': bars_data[5][i_day_start: i_day_end]
                    })

                day_data.fix_errors(day_date)
                day_data.check_day_data(symbol, timeframe, day_date)

            self.save_to_cache_verified(symbol, timeframe, day_data, day_date)
            downloaded_days.append(day_data)

            if is_incomplete_day:
                break

            day_date += 1

        self.count_datasource_get += 1
        return downloaded_days

    @staticmethod
    def append_series_from_day_data(day_data, series):
        td_time, td_open, td_high, td_low, td_close, td_volume = series
        td_time.append(day_data.time)
        td_open.append(day_data.open)
        td_high.append(day_data.high)
        td_low.append(day_data.low)
        td_close.append(day_data.close)
        td_volume.append(day_data.volume)

    def download_days_to_series(self, symbol, timeframe, date_start, date_end, day_for_grow, series):
        assert date_start.dtype == 'datetime64[D]'
        assert date_end.dtype == 'datetime64[D]'

        intermediate_save_days = max(int(BARS_FOR_INTERMEDIATE_SAVE / TIME_UNITS_IN_ONE_DAY * timeframe.value), 1)
        date_from = date_start
        while date_from <= date_end:
            date_to = min(date_from + intermediate_save_days - 1, date_end)
            downloaded_days = self.download_days(symbol, timeframe, date_from, date_to, day_for_grow)
            date_from = date_to + 1
            for downloaded_day_data in downloaded_days:
                self.append_series_from_day_data(downloaded_day_data, series)
                if downloaded_day_data.is_incomplete_day:
                    date_from = date_end + 1
                    break

        return downloaded_day_data.is_incomplete_day

    def get_bar_data(self, symbol, timeframe, time_begin, time_end, day_for_grow=None):
        assert time_begin is not None
        assert time_end is not None
        assert time_begin <= time_end

        if time_begin < self.online_source.history_start:
            raise LTIExceptionBadTimeParameter(f'A very early date for {self.datasource_id}: {time_begin}')

        series = [], [], [], [], [], []
        date_end = time_end.astype('datetime64[D]')
        day_date = time_begin.astype('datetime64[D]')

        is_live = False
        start_day_for_download = None
        while day_date <= date_end:

            day_data = self.bars_of_day_from_cache(symbol, timeframe, day_date)
            if day_data is None:
                if start_day_for_download is None:
                    start_day_for_download = day_date
                day_date += 1
                continue

            if start_day_for_download is not None:
                last_day_is_incomplete = self.download_days_to_series(symbol, timeframe, start_day_for_download,
                                                                      day_date - 1, day_for_grow, series)
                assert not last_day_is_incomplete
                start_day_for_download = None

            self.append_series_from_day_data(day_data, series)
            day_date += 1

        if start_day_for_download is not None:
            is_live = self.download_days_to_series(symbol, timeframe, start_day_for_download,
                                                                  day_date - 1, day_for_grow, series)

        td_time, td_open, td_high, td_low, td_close, td_volume = series
        if len(td_time) == 0:
            raise LTIExceptionEmptyBarData()

        return OHLCV_data({'symbol': symbol,
                           'timeframe': timeframe,
                           'source': self.datasource_id,
                           'is_live': is_live,
                           'time': np.hstack(td_time),
                           'open': np.hstack(td_open),
                           'high': np.hstack(td_high),
                           'low': np.hstack(td_low),
                           'close': np.hstack(td_close),
                           'volume': np.hstack(td_volume)})
