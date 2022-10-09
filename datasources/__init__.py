import os.path as path
from common import *


class TimeframeData:

    def __init__(self, datasource_module, **kwargs):

        cash_folder = kwargs.get('timeframe_data_path')
        if cash_folder is None:
            self.cash_folder = os.path.join(timeframe_data_path, datasource_module.datasource_name())

        datasource_module.init()
        self.datasource_module = datasource_module

    def timeframe_day_data(self, symbol, timeframe, date):

        filename = self.filename_day_data(symbol, timeframe, date)
        if path.isfile(filename):
            return self.load_cash_data(filename)

        day_data = self.datasource_module.timeframe_day_data(symbol, timeframe, date)
        self.save_to_cash(filename, day_data)

        return day_data

    def timeframe_data(self, symbol, timeframe, date_begin, date_end):
        pass



