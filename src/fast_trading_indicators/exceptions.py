
class FTIException(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        if self.message:
            return f'{self.__class__.__name__}: {self.message}'
        else:
            return self.__class__.__name__


class FTIExceptionBadSourceData(FTIException):

    def __init__(self, data_error_message, source=None, symbol=None, day_date=None):
        self.source = source
        self.symbol = symbol
        self.date = day_date
        self.data_error_message = data_error_message
        super().__init__(f'Bad source data (source {source}, symbol {symbol}, date {day_date.date()}')


class FTIExceptionTooManyEmptyBars(FTIException):

    def __init__(self, source_name, symbol, timeframe, first_bar_time, end_bar_time, fraction, consecutive):
        self.source_name = source_name
        self.symbol = symbol
        self.timeframe = timeframe
        self.first_bar_time = first_bar_time
        self.end_bar_time = end_bar_time
        self.fraction = fraction
        self.consecutive = consecutive

        super().__init__(
            f'Too many empty bars: fraction {fraction}, consecutive {consecutive}. '
            f'Source {source_name}, symbol {symbol}, timeframe {timeframe}, date {first_bar_time} - {end_bar_time}.')


class FTISourceDataNotFound(FTIException):

    def __init__(self, symbol, date):
        self.symbol = symbol
        self.date = date

        super().__init__(f'Source data not found! Symbol {self.symbol}, date {self.date.date()}.')

