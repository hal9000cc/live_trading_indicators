

class LTIException(Exception):
    pass


class LTIBadTimeParameter(LTIException):
    def __init__(self, value):
        self.value = value
        super().__init__(f'Bad date or time value: {value}')


class LTIExceptionSymbolNotFound(LTIException):
    def __init__(self, symbol):
        self.symbol = symbol
        super().__init__(f'Symbol not found: {symbol}')


class LTIBadTimeframeParameter(LTIException):
    def __init__(self, value):
        self.value = value
        super().__init__(f'Bad timeframe value: {value}')


class LTIExceptionBadSourceData(LTIException):
    def __init__(self, data_error_message, source=None, symbol=None, day_date=None):
        self.source = source
        self.symbol = symbol
        self.date = day_date
        self.data_error_message = data_error_message
        super().__init__(f'Bad source data (source {source}, symbol {symbol}, date {day_date.date()}')


class LTIExceptionTooManyEmptyBars(LTIException):
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


class LTIExceptionSourceDataNotFound(LTIException):
    def __init__(self, symbol, date):
        self.symbol = symbol
        self.date = date
        super().__init__(f'Source data not found! Symbol {self.symbol}, date {self.date}.')


class LTIExceptionIndicatorNotFound(LTIException):
    def __init__(self, indicator_name):
        self.indicator_name = indicator_name
        super().__init__(f'Indicator "{self.indicator_name}" not found.')


class LTIExceptionOutOfThePeriod(LTIException):
    def __init__(self):
        super().__init__('Time out of the calculation period')


class LTIExceptionBadDatasource(LTIException):
    def __init__(self, source):
        self.source = source
        super().__init__(f'Bad source: {source}')
