import os
import os.path as path
import construct as cs
import zlib
import logging
from ..exceptions import *
from .bars_cache import BarsCache
from ..indicator_data import *
from ..constants import PRICE_TYPE, VOLUME_TYPE


BLOCK_FILE_SIGNATURE = b'LTI'
BLOCK_FILE_EXT = 'lti'
BLOCK_FILE_VERSION = 1

CACHE_BLOCK_VERSION = 2

DAYS_WAIT_FOR_ENTIRE = 30
MAX_CLIENT_TIME_ERROR = TIME_UNITS_IN_ONE_SECOND * 60 * 15


class SourceData:

    def __init__(self, datasource_module, config):

        self.config = config
        self.cach_folder = path.join(self.config['cache_folder'], datasource_module.datasource_name())

        self.datasource_module = datasource_module

        self.count_datasource_get = 0
        self.count_datasource_bars_get = 0
        self.count_file_load = 0

        self.bars_cache = BarsCache()

    def __del__(self):
        del self.bars_cache

    def filename_day_data(self, symbol, timeframe, day_date):
        assert type(day_date) == np.datetime64 and day_date.dtype.name == 'datetime64[D]'

        store_folder, symbol_store_name = self.datasource_module.get_store_names(symbol)
        if store_folder:
            folder = path.join(self.cach_folder, store_folder)
        else:
            folder = self.cach_folder

        filename = f'{symbol_store_name}-{timeframe}-{day_date}.{BLOCK_FILE_EXT}'
        return folder, filename, symbol_store_name

    @staticmethod
    def rename_file_force(source, destination):

        if path.isfile(destination):
            os.remove(destination)

        os.rename(source, destination)

    @staticmethod
    def get_file_signature_struct():
        return cs.Struct('signature' / cs.Const(BLOCK_FILE_SIGNATURE), 'file_version' / cs.Int16ub)

    @staticmethod
    def build_signature_and_version():
        return __class__.get_file_signature_struct().build({'file_version': BLOCK_FILE_VERSION})

    @staticmethod
    def parse_signature_and_version(stream):
        return __class__.get_file_signature_struct().parse_stream(stream)

    @staticmethod
    def get_header_struct_v1():
        return cs.Struct(
            'n_bars' / cs.Int
        )

    @staticmethod
    def build_header_v1(day_data):

        header = {
            'n_bars': len(day_data.time)
        }

        return __class__.get_header_struct_v1().build(header)

    def build_header(self, day_data):

        if BLOCK_FILE_VERSION == 1:
            return self.build_header_v1(day_data)

        raise NotImplementedError()

    @staticmethod
    def parse_header(file, file_version):

        if file_version == 1:
            header_struct = __class__.get_header_struct_v1()
        else:
            raise NotImplementedError()

        return header_struct.sizeof(), header_struct.parse(file)

    @staticmethod
    def get_file_data_struct(n_bars):
        return cs.Struct(

            'time' / cs.Long[n_bars],
            'open' / cs.Double[n_bars],
            'high' / cs.Double[n_bars],
            'low' / cs.Double[n_bars],
            'close' / cs.Double[n_bars],
            'volume' / cs.Double[n_bars]
        )

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

    def load_from_cache(self, file_name, symbol, timeframe):

        with open(file_name, 'rb') as file:

            signature_and_version = self.parse_signature_and_version(file)
            if signature_and_version.signature != BLOCK_FILE_SIGNATURE:
                raise LTIException('Bad data cash file')

            buf = zlib.decompress(file.read())
            header_len, header = self.parse_header(buf, signature_and_version.file_version)
            data_struct = self.get_file_data_struct(header.n_bars)
            file_data = data_struct.parse(buf[header_len:])

        return OHLCV_day({
            'symbol': symbol,
            'timeframe': timeframe,
            'is_incomplete_day': False,
            'time': np.array(file_data.time, dtype=np.int64).astype(TIME_TYPE),
            'open': np.array(file_data.open, dtype=PRICE_TYPE),
            'high': np.array(file_data.high, dtype=PRICE_TYPE),
            'low': np.array(file_data.low, dtype=PRICE_TYPE),
            'close': np.array(file_data.close, dtype=PRICE_TYPE),
            'volume': np.array(file_data.volume, dtype=VOLUME_TYPE)
        })


    def save_to_cache_verified(self, symbol, timeframe, bar_data, day_date):

        now = np.datetime64(dt.datetime.now(), TIME_TYPE_UNIT)

        if bar_data.is_incomplete_day:
            return

        if bar_data.is_empty():
            return

        if not bar_data.is_entire():
            if (np.datetime64(now, 'D') - day_date).astype(np.int64) < DAYS_WAIT_FOR_ENTIRE:
                return

        assert timeframe.begin_of_tf(np.datetime64(day_date, TIME_TYPE_UNIT) + TIME_UNITS_IN_ONE_DAY) + timeframe.value + MAX_CLIENT_TIME_ERROR < now
        self.save_to_blocks_cache(symbol, timeframe, day_date, bar_data)

    @staticmethod
    def block_header_struct():
        return cs.Struct(
            'block_version' / cs.Int8ub,
            'n_bars' / cs.Int32ub
        )

    @staticmethod
    def block_data_struct(n_bars):
        return cs.Struct(
            'time' / cs.Long[n_bars],
            'open' / cs.Double[n_bars],
            'high' / cs.Double[n_bars],
            'low' / cs.Double[n_bars],
            'close' / cs.Double[n_bars],
            'volume' / cs.Double[n_bars]
        )

    def save_to_blocks_cache(self, symbol, timeframe, day_date, bar_data):

        folder, file_name, symbol_store_name = self.filename_day_data(symbol, timeframe, day_date)

        n_bars = len(bar_data)
        block_header_struct = self.block_header_struct()
        block_data_struct = self.block_data_struct(n_bars)
        buf_data = [
            block_header_struct.build({'block_version': CACHE_BLOCK_VERSION, 'n_bars': n_bars}),
            block_data_struct.build({
                'n_bars': len(bar_data),
                'time': bar_data.time.astype(np.int64),
                'open': bar_data.open,
                'high': bar_data.high,
                'low': bar_data.low,
                'close': bar_data.close,
                'volume': bar_data.volume
            })]

        self.bars_cache.day_save(folder, symbol_store_name, timeframe, day_date, b''.join(buf_data))

    def load_from_blocks_cache(self, symbol, timeframe, day_date):

        folder, file_name, symbol_store_name = self.filename_day_data(symbol, timeframe, day_date)

        bar_saved_data = self.bars_cache.day_load(folder, symbol_store_name, timeframe, day_date)
        if bar_saved_data is None:
            return None

        block_header_struct = self.block_header_struct()
        block_header = block_header_struct.parse(bar_saved_data[: block_header_struct.sizeof()])

        if block_header.block_version != CACHE_BLOCK_VERSION:
            raise NotImplemented(f'Unsupported block version: {block_header.block_version}')

        block_data = self.block_data_struct(block_header.n_bars).parse(bar_saved_data[block_header_struct.sizeof():])

        return OHLCV_day({
            'symbol': symbol,
            'timeframe': timeframe,
            'is_incomplete_day': False,
            'time': np.array(block_data.time, dtype=np.int64).astype(TIME_TYPE),
            'open': np.array(block_data.open, dtype=PRICE_TYPE),
            'high': np.array(block_data.high, dtype=PRICE_TYPE),
            'low': np.array(block_data.low, dtype=PRICE_TYPE),
            'close': np.array(block_data.close, dtype=PRICE_TYPE),
            'volume': np.array(block_data.volume, dtype=VOLUME_TYPE)
        })

    def bars_of_day_from_cache(self, symbol, timeframe, day_date):

        folder, file_name, _ = self.filename_day_data(symbol, timeframe, day_date)

        old_cach_file = path.join(folder, file_name)
        if path.isfile(old_cach_file):

            bar_data = self.load_from_cache(old_cach_file, symbol, timeframe)
            self.save_to_blocks_cache(symbol, timeframe, day_date, bar_data)
            os.remove(old_cach_file)

            self.count_file_load += 1
            return bar_data

        bar_data = self.load_from_blocks_cache(symbol, timeframe, day_date)
        if bar_data is not None:
            self.count_file_load += 1

        return bar_data

    def bars_online_request_with_grow(self, symbol, timeframe, query_time_start, query_time_end, day_for_grow):

        if day_for_grow is not None and day_for_grow.time[0] == query_time_start:
            query_time_start = day_for_grow.time[-1]
            bars_data = self.datasource_module.bars_online_request(symbol, timeframe, query_time_start, query_time_end)
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
            bars_data = self.datasource_module.bars_online_request(symbol, timeframe, query_time_start, query_time_end)
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
            i_day_start = np.searchsorted(bars_data[0], time_start_day)
            i_day_end = np.searchsorted(bars_data[0], time_end_day)

            is_incomplete_day = i_day_end >= len(bars_data[0]) and len(bars_data[0]) > 0 and bars_data[0][-1] >= last_bar_time_of_timeframe

            day_data = OHLCV_day({
                'symbol': symbol,
                'timeframe': timeframe,
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
    def append_series_from_day_data(day_data, td_time, td_open, td_high, td_low, td_close, td_volume):
        td_time.append(day_data.time)
        td_open.append(day_data.open)
        td_high.append(day_data.high)
        td_low.append(day_data.low)
        td_close.append(day_data.close)
        td_volume.append(day_data.volume)

    def get_bar_data(self, symbol, timeframe, time_begin, time_end, day_for_grow=None):
        assert time_begin is not None
        assert time_end is not None
        assert time_end >= time_begin

        td_time, td_open, td_high, td_low, td_close, td_volume = [], [], [], [], [], []
        date_end = time_end.astype('datetime64[D]')
        day_date = time_begin.astype('datetime64[D]')

        try:

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
                    downloaded_days = self.download_days(symbol, timeframe, start_day_for_download, day_date - 1, day_for_grow)
                    assert not downloaded_days[-1].is_incomplete_day
                    start_day_for_download = None
                    for downloaded_day_data in downloaded_days:
                        self.append_series_from_day_data(downloaded_day_data, td_time,
                                                         td_open, td_high, td_low, td_close, td_volume)

                self.append_series_from_day_data(day_data, td_time, td_open, td_high, td_low, td_close, td_volume)
                day_date += 1

            if start_day_for_download is not None:
                downloaded_days = self.download_days(symbol, timeframe, start_day_for_download, day_date - 1, day_for_grow)
                for downloaded_day_data in downloaded_days:
                    self.append_series_from_day_data(downloaded_day_data, td_time,
                                                     td_open, td_high, td_low, td_close, td_volume)
                    if downloaded_day_data.is_incomplete_day:
                        is_live = True

        finally:
            self.bars_cache.close_block_file()

        if len(td_time) == 0:
            raise LTIExceptionEmptyBarData()

        return OHLCV_data({'symbol': symbol,
                           'timeframe': timeframe,
                           'is_live': is_live,
                           'time': np.hstack(td_time),
                           'open': np.hstack(td_open),
                           'high': np.hstack(td_high),
                           'low': np.hstack(td_low),
                           'close': np.hstack(td_close),
                           'volume': np.hstack(td_volume)})
