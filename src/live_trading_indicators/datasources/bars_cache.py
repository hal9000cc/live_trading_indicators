import numpy as np
import os.path as path
from enum import Enum
from .blocks_cache import BlockCache
from ..constants import TIME_UNITS_IN_ONE_SECOND


class BarsCache(BlockCache):

    def __init__(self):
        super().__init__(b'LTC')

    @staticmethod
    def get_symbol_name(symbol):
        return symbol.split('/')[-1]

    def get_store_params(self, symbol, timeframe, date):
        assert date.dtype.name == 'datetime64[D]'

        symbol_name = self.get_symbol_name(symbol)

        if timeframe.value < TIME_UNITS_IN_ONE_SECOND * 60:
            raise NotImplemented()
        elif timeframe.value < TIME_UNITS_IN_ONE_SECOND * 60 * 60:
            date_month = np.datetime64(date, 'M')
            days_in_month = ((date_month + 1).astype('datetime64[D]') - date_month).astype(int)
            day_index = (date - date_month).astype('timedelta64[D]').astype(int)
            return f'{symbol_name}-{timeframe}-{date_month}.ltc', int(days_in_month), int(day_index)
        else:
            date_year = np.datetime64(date, 'Y')
            days_in_year = ((date_year + 1) - date_year).astype('timedelta64[D]').astype(int)
            day_index = (date - date_year).astype('timedelta64[D]').astype(int)
            return f'{symbol_name}-{timeframe}-{date_year}.ltc', int(days_in_year), int(day_index)

    def day_save(self, folder, symbol, timeframe, date, data):

        file_name, days_in_file, day_index = self.get_store_params(symbol, timeframe, date)

        self.save_block(path.join(folder, file_name), day_index, days_in_file, data)

    def day_load(self, folder, symbol, timeframe, date):

        file_name, days_in_file, day_index = self.get_store_params(symbol, timeframe, date)

        return self.load_block(path.join(folder, file_name), day_index)


