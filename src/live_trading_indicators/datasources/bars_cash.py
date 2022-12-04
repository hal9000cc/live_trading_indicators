import numpy as np
import os.path as path
from enum import Enum
from blocks_cach import BlockCash
from ..constants import TIME_UNITS_IN_ONE_SECOND


class BarsCach(BlockCash):

    def __init__(self):
        super().__init__('LTC')

    @staticmethod
    def get_symbol_name(symbol):
        return symbol.split('/')[-1]

    def get_store_params(self, symbol, timeframe, date):

        symbol_name = self.get_symbol_name(symbol)

        if timeframe.value < TIME_UNITS_IN_ONE_SECOND * 60:
            raise NotImplemented()
        elif timeframe.value < TIME_UNITS_IN_ONE_SECOND * 60 * 60:
            date_month = np.datetime64(date, 'M')
            days_in_month = ((date_month + 1) - date_month).astype('timedelta64[D]').astype(int)
            day_index = (date - date_month).astype('timedelta64[D]').astype(int)
            return f'{symbol_name}-{timeframe}-{date_month}.ltc', days_in_month, day_index
        else:
            date_year = np.datetime64(date, 'Y')
            days_in_year = ((date_year + 1) - date_year).astype('timedelta64[D]').astype(int)
            day_index = (date - date_year).astype('timedelta64[D]').astype(int)
            return f'{symbol_name}-{timeframe}-{date_year}.ltc', days_in_year, day_index

    def day_save(self, folder, symbol, timeframe, date, data):

        file_name, days_in_file, day_index = self.get_store_params(symbol, timeframe, date)

        self.save_block(path.join(folder, file_name), day_index, days_in_file)

    def day_load(self, folder, symbol, timeframe, date):

        file_name, days_in_file, day_index = self.get_store_params(symbol, timeframe, date)

        return self.load_block(path.join(folder, file_name), day_index)


