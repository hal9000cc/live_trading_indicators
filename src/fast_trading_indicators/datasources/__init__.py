import datetime as dt
import os
import os.path as path
import numpy as np
import construct as cs
import zlib
import logging
from ..common import *

CASH_FILE_SIGNATURE = b'FTI'
CASH_FILE_VERSION = 1


class TimeframeData:

    def __init__(self, datasource_module, common_data_path=None):

        self.cash_folder = path.join(DEFAULT_DATA_PATH if common_data_path is None else common_data_path,
                                                                'timeframe_data', datasource_module.datasource_name())

        datasource_module.init(common_data_path)
        self.datasource_module = datasource_module

    def filename_day_data(self, symbol, timeframe, day_date):
        symbol_parts = symbol.split('/')
        filename = f'{symbol_parts[-1]}-{timeframe}-{day_date.date()}.ftid'
        return path.join(self.cash_folder, *symbol_parts[:-1], filename)

    def get_timeframe_day_data(self, symbol, timeframe, day_date):

        filename = self.filename_day_data(symbol, timeframe, day_date)
        if path.isfile(filename):
            day_data = self.load_from_cash(filename)
        else:
            day_data = self.datasource_module.timeframe_day_data(symbol, timeframe, day_date)
            self.check_day_data(day_data, symbol, timeframe, day_date)
            self.save_to_cash(filename, day_data)

        return day_data

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

    def save_to_cash(self, file_name, day_data):

        n_bars = len(day_data.time)

        data_struct = self.get_file_data_struct(n_bars)
        buf_data = data_struct.build({
            'time': day_data.time.astype(int),
            'open': day_data.open,
            'high': day_data.high,
            'low': day_data.low,
            'close': day_data.close,
            'volume': day_data.volume
        })

        file_folder = path.split(file_name)[0]
        if not path.isdir(file_folder):
            os.makedirs(file_folder)

        with open(file_name, 'wb') as file:
            file.write(self.build_signature_and_version())
            file.write(self.build_header(day_data))
            file.write(zlib.compress(buf_data))

    def load_from_cash(self, file_name):

        with open(file_name, 'rb') as file:

            signature_and_version = self.parse_signature_and_version(file)
            if signature_and_version.signature != CASH_FILE_SIGNATURE:
                raise FTIException('Bad cash file')

            header = self.parse_header(file, signature_and_version.file_version)

            buf = zlib.decompress(file.read())
            data_struct = self.get_file_data_struct(header.n_bars)
            file_data = data_struct.parse(buf)

        return IndicatorData({
            'time': np.array(file_data.time, dtype=int).astype(TIME_TYPE),
            'open': np.array(file_data.open, dtype=PRICE_TYPE),
            'high': np.array(file_data.high, dtype=PRICE_TYPE),
            'low': np.array(file_data.low, dtype=PRICE_TYPE),
            'close': np.array(file_data.close, dtype=PRICE_TYPE),
            'volume': np.array(file_data.volume, dtype=VOLUME_TYPE)
        })

    def get_timeframe_data(self, symbol, timeframe, date_begin, date_end):

        if date_begin is None:
            raise FTIException('No begin_date set')

        if date_end is None:
            raise FTIException('No end_date set')

        td_time, td_open, td_high, td_low, td_close, td_volume = [], [], [], [], [], []
        day_date = date_begin
        while day_date <= date_end:
            day_data = self.get_timeframe_day_data(symbol, timeframe, day_date)
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


def ticks_2_timeframe_data(tick_data, timeframe, date):

    assert date.time() == dt.time()

    day_start_ms = np.datetime64(date).astype('datetime64[ms]').astype(int)
    step_ms = timeframe.value * 1000
    n_candles = 24 * 60 * 60 // timeframe.value

    tick_time, tick_price, tick_volumes = tick_data.time, tick_data.price, tick_data.volume

    if len(tick_price) == 0: raise FTIExceptionBadSourceData('Empty day, no ticks')
    if (tick_time[:-1] > tick_time[1:]).any(): raise FTIExceptionBadSourceData('Non-ordered ticks time')

    first_price = tick_price[0]

    timeframe_starts = (day_start_ms + np.arange(n_candles) * step_ms).astype('datetime64[ms]')
    ix_tf_end = np.searchsorted(tick_time, timeframe_starts)[1:]
    interval_prices = np.split(tick_price, ix_tf_end)
    interval_volumes = np.split(tick_volumes, ix_tf_end)

    tf_open, tf_high, tf_low, tf_close, tf_volume =\
        np.zeros(n_candles, dtype=PRICE_TYPE),\
        np.zeros(n_candles, dtype=PRICE_TYPE),\
        np.zeros(n_candles, dtype=PRICE_TYPE),\
        np.zeros(n_candles, dtype=PRICE_TYPE),\
        np.zeros(n_candles, dtype=VOLUME_TYPE)

    tf_time = timeframe_starts

    for i_tf in range(n_candles):

        if len(interval_prices[i_tf]) == 0: continue

        tf_open[i_tf] = interval_prices[i_tf][0]
        tf_high[i_tf] = interval_prices[i_tf].max()
        tf_low[i_tf] = interval_prices[i_tf].min()
        tf_close[i_tf] = interval_prices[i_tf][-1]
        tf_volume[i_tf] = interval_volumes[i_tf].sum()

    return IndicatorData({
        'time': tf_time,
        'open': tf_open,
        'high': tf_high,
        'low': tf_low,
        'close': tf_close,
        'volume': tf_volume
    })