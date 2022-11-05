import os
import os.path as path
import construct as cs
import zlib
import logging
from ..exceptions import *
from ..indicator_data import *
from ..constants import PRICE_TYPE, VOLUME_TYPE


CASH_FILE_SIGNATURE = b'LTI'
CASH_FILE_EXT = 'lti'
CASH_FILE_VERSION = 1

DAYS_WAIT_FOR_ENTIRE = 30


class SourceData:

    def __init__(self, datasource_module, config):

        self.config = config # config_load()
        self.cash_folder = path.join(self.config['cash_folder'], datasource_module.datasource_name())

        self.datasource_module = datasource_module

        if hasattr(datasource_module, 'DEFAULT_SYMBOL_PART'):
            self.default_symbol_part_for_path = datasource_module.DEFAULT_SYMBOL_PART
        else:
            self.default_symbol_part_for_path = ''

        self.count_datasource_get = 0
        self.count_file_load = 0

    def filename_day_data(self, symbol, timeframe, day_date):
        assert type(day_date) == np.datetime64 and day_date.dtype.name == 'datetime64[D]'

        symbol_parts = symbol.split('/')

        if len(symbol_parts) < 2:
            symbol_parts = [self.default_symbol_part_for_path] + symbol_parts

        filename = f'{symbol_parts[-1]}-{timeframe}-{day_date}.{CASH_FILE_EXT}'
        return path.join(self.cash_folder, *symbol_parts[:-1], filename)

    def bars_of_day(self, symbol, timeframe, day_date, bar_for_grow=None):

        filename = self.filename_day_data(symbol, timeframe, day_date)
        if path.isfile(filename):
            self.count_file_load += 1
            bar_data = self.load_from_cash(filename, symbol, timeframe)
        else:

            self.count_datasource_get += 1

            bar_data = self.datasource_module.bars_of_day(
                symbol, timeframe,
                day_date,
                bar_for_grow if bar_for_grow is not None and bar_for_grow.time[0] == day_date else None)

            bar_data.check_day_data(symbol, timeframe, day_date)
            self.save_to_cash_verified(filename, bar_data, day_date)

        return bar_data

    @staticmethod
    def rename_file_force(source, destination):

        if path.isfile(destination):
            os.remove(destination)

        os.rename(source, destination)

    @staticmethod
    def get_file_signature_struct():
        return cs.Struct('signature' / cs.Const(CASH_FILE_SIGNATURE), 'file_version' / cs.Int16ub)

    @staticmethod
    def build_signature_and_version():
        return __class__.get_file_signature_struct().build({'file_version': CASH_FILE_VERSION})

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

        if CASH_FILE_VERSION == 1:
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

    def save_to_cash(self, file_name, bar_data):

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

    def load_from_cash(self, file_name, symbol, timeframe):

        with open(file_name, 'rb') as file:

            signature_and_version = self.parse_signature_and_version(file)
            if signature_and_version.signature != CASH_FILE_SIGNATURE:
                raise LTIException('Bad data cash file')

            buf = zlib.decompress(file.read())
            header_len, header = self.parse_header(buf, signature_and_version.file_version)
            data_struct = self.get_file_data_struct(header.n_bars)
            file_data = data_struct.parse(buf[header_len:])

        return OHLCV_day({
            'symbol': symbol,
            'timeframe': timeframe,
            'is_live_day': False,
            'time': np.array(file_data.time, dtype=np.int64).astype(TIME_TYPE),
            'open': np.array(file_data.open, dtype=PRICE_TYPE),
            'high': np.array(file_data.high, dtype=PRICE_TYPE),
            'low': np.array(file_data.low, dtype=PRICE_TYPE),
            'close': np.array(file_data.close, dtype=PRICE_TYPE),
            'volume': np.array(file_data.volume, dtype=VOLUME_TYPE)
        })

    def save_to_cash_verified(self, filename, bar_data, day_date):

        now = dt.datetime.now()

        if bar_data.is_live_day:
            return

        if bar_data.is_empty():
            return

        if not bar_data.is_entire():
            if (np.datetime64(now, 'D') - day_date).astype(np.int64) < DAYS_WAIT_FOR_ENTIRE:
                return

        self.save_to_cash(filename, bar_data)

    def get_bar_data(self, symbol, timeframe, time_begin, time_end, day_for_grow=None):

        assert time_begin is not None
        assert time_end is not None
        assert time_end >= time_begin

        td_time, td_open, td_high, td_low, td_close, td_volume = [], [], [], [], [], []
        day_dates = []
        date_end = time_end.astype('datetime64[D]')
        day_date = time_begin.astype('datetime64[D]')
        while day_date <= date_end:
            day_dates.append(day_date)
            day_date += 1

        is_live = False
        for day_date in day_dates:
            day_data = self.bars_of_day(symbol, timeframe, day_date, day_for_grow)
            td_time.append(day_data.time)
            td_open.append(day_data.open)
            td_high.append(day_data.high)
            td_low.append(day_data.low)
            td_close.append(day_data.close)
            td_volume.append(day_data.volume)
            if day_data.is_live_day:
                is_live = True
                break

        return OHLCV_data({'symbol': symbol,
                           'timeframe': timeframe,
                           'is_live': is_live,
                           'time': np.hstack(td_time),
                           'open': np.hstack(td_open),
                           'high': np.hstack(td_high),
                           'low': np.hstack(td_low),
                           'close': np.hstack(td_close),
                           'volume': np.hstack(td_volume)})
