import datetime as dt
import os
import os.path as path
import numpy as np
import construct as cs
import zlib
from zipfile import ZipFile
import logging
from ..common import *
from ..exceptions import *
from ..indicator_data import *


CASH_FILE_SIGNATURE = b'FTI'
CASH_FILE_VERSION = 1


class SourceData:

    def __init__(self, datasource_module, config):

        self.config = config # config_load()
        self.cash_folder = path.join(self.config['cash_folder'], datasource_module.datasource_name())

        self.datasource_module = datasource_module

    def filename_day_data(self, symbol, timeframe, day_date):
        symbol_parts = symbol.split('/')
        filename = f'{symbol_parts[-1]}-{timeframe}-{day_date.date()}.ftid'
        return path.join(self.cash_folder, *symbol_parts[:-1], filename)

    def bars_of_day(self, symbol, timeframe, day_date):

        filename = self.filename_day_data(symbol, timeframe, day_date)
        if path.isfile(filename):
            bar_data = self.load_from_cash(filename, symbol, timeframe)
        else:
            bar_data = self.datasource_module.bars_of_day(symbol, timeframe, day_date)
            self.check_day_data(bar_data, symbol, timeframe, day_date)
            if not bar_data.is_empty():
                self.save_to_cash(filename, bar_data)

        return bar_data

    @staticmethod
    def check_day_data(day_data, symbol, timeframe, day_date):

        error = None
        first_time = day_data.time[0]
        n_bars = 24 * 60 * 60 // timeframe.value

        if not(len(day_data.time) == n_bars and
               len(day_data.open) == n_bars and
               len(day_data.high) == n_bars and
               len(day_data.low) == n_bars and
               len(day_data.close) == n_bars and
               len(day_data.volume) == n_bars):
            error = 'bad data length'

        if first_time != np.datetime64(day_date).astype(TIME_TYPE):
            error = 'bad first bar time'

        if (first_time + np.arange(n_bars) * timeframe.value * 1000 != day_data.time).any():
            error = 'bad bars time'

        if (day_data.high < day_data.low).any():
            error = 'bad high/low values'

        if (day_data.open > day_data.high).any() or (day_data.open < day_data.low).any():
            error = 'bad open values'

        if (day_data.close > day_data.high).any() or (day_data.close < day_data.low).any():
            error = 'bad close values'

        if (day_data.volume < 0).any():
            error = 'bad volume values'

        nonzero_volume = day_data.volume > 0

        if (nonzero_volume & (day_data.open <= 0)).any():
            error = 'bad open values'

        if (nonzero_volume & (day_data.close <= 0)).any():
            error = 'bad close values'

        if error:
            raise FTIException(f'Timeframe data error: {error}')

    @staticmethod
    def get_file_signature_struct():
        return cs.Struct('signature' / cs.Const(CASH_FILE_SIGNATURE), 'file_version' / cs.Int)

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

        raise NotImplementedError

    @staticmethod
    def parse_header(file, file_version):

        if file_version == 1:
            return __class__.get_header_struct_v1().parse_stream(file)

        raise NotImplementedError

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
        buf_data = data_struct.build({
            'time': bar_data.time.astype(int),
            'open': bar_data.open,
            'high': bar_data.high,
            'low': bar_data.low,
            'close': bar_data.close,
            'volume': bar_data.volume
        })

        file_folder = path.split(file_name)[0]
        if not path.isdir(file_folder):
            os.makedirs(file_folder)

        temp_file_name = f'{file_name}.tmp'
        with open(temp_file_name, 'wb') as file:
            file.write(self.build_signature_and_version())
            file.write(self.build_header(bar_data))
            file.write(zlib.compress(buf_data))
        rename_file_force(temp_file_name, file_name)

    def load_from_cash(self, file_name, symbol, timeframe):

        with open(file_name, 'rb') as file:

            signature_and_version = self.parse_signature_and_version(file)
            if signature_and_version.signature != CASH_FILE_SIGNATURE:
                raise FTIException('Bad cash file')

            header = self.parse_header(file, signature_and_version.file_version)

            buf = zlib.decompress(file.read())
            data_struct = self.get_file_data_struct(header.n_bars)
            file_data = data_struct.parse(buf)

        return OHLCV_data({
            'symbol': symbol,
            'timeframe': timeframe,
            'time': np.array(file_data.time, dtype=int).astype(TIME_TYPE),
            'open': np.array(file_data.open, dtype=PRICE_TYPE),
            'high': np.array(file_data.high, dtype=PRICE_TYPE),
            'low': np.array(file_data.low, dtype=PRICE_TYPE),
            'close': np.array(file_data.close, dtype=PRICE_TYPE),
            'volume': np.array(file_data.volume, dtype=VOLUME_TYPE)
        })

    def get_bar_data(self, symbol, timeframe, date_begin, date_end):

        if date_begin is None:
            raise FTIException('No begin_date set')

        if date_end is None:
            raise FTIException('No end_date set')

        if date_begin > date_end:
            raise ValueError('begin_date less then end_date')

        td_time, td_open, td_high, td_low, td_close, td_volume = [], [], [], [], [], []
        day_date = date_begin
        while day_date <= date_end:
            day_data = self.bars_of_day(symbol, timeframe, day_date)
            td_time.append(day_data.time)
            td_open.append(day_data.open)
            td_high.append(day_data.high)
            td_low.append(day_data.low)
            td_close.append(day_data.close)
            td_volume.append(day_data.volume)
            day_date += dt.timedelta(days=1)

        return IndicatorData({  'symbol': symbol,
                                'timeframe': timeframe,
                                'time': np.hstack(td_time),
                                'open': np.hstack(td_open),
                                'high': np.hstack(td_high),
                                'low': np.hstack(td_low),
                                'close': np.hstack(td_close),
                                'volume': np.hstack(td_volume)
                             })


def rename_file_force(source, destination):

    if path.isfile(destination):
        os.remove(destination)

    os.rename(source, destination)


def byte_csv_to_strings(csv_text):

    max_line_length = 200
    for i in range(10):
        first_lines = csv_text[:max_line_length * 2].splitlines()
        if len(first_lines) > 2: break
    else:
        FTIException(f'Bad csv file: {file_name}')

    n_columns = first_lines[1].count(b',') + 1

    return np.array(csv_text.replace(b',', b'\n').splitlines()).reshape((-1, n_columns))


def read_zipcsv_to_strings(source):

    with ZipFile(source) as zip_file:
        csv_text = zip_file.read(zip_file.namelist()[0])

    return byte_csv_to_strings(csv_text)


