

class LTIException(Exception):
    pass


class LTIExceptionBadOfflineDataSource(Exception):
    def __init__(self, reason):
        super().__init__(f'Bad offline data source: {reason}')


class LTIExceptionBadTimeParameter(LTIException):
    def __init__(self, value):
        self.value = value
        super().__init__(f'Bad date or time value: {value}')


class LTIExceptionSymbolNotFound(LTIException):
    def __init__(self, symbol):
        self.symbol = symbol
        super().__init__(f'Symbol not found: {symbol}')


class LTIExceptionEmptyBarData(LTIException):
    def __init__(self):
        super().__init__('Empty bar data')


class LTIExceptionBadTimeframeValue(LTIException):
    def __init__(self, value):
        self.value = value
        super().__init__(f'Bad timeframe value: {value}')


class LTIExceptionTimeBeginLaterTimeEnd(LTIException):
    def _init_(self, time_begin, time_end):
        self.time_begin = time_begin
        self.time_end = time_end
        super().__init__(f'Time begin is later than time end ({time_begin} < {time_end}')


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
        super().__init__('Time out of the work period')


class LTIExceptionBadDatasource(LTIException):
    def __init__(self, source):
        self.source = source
        super().__init__(f'Bad source: {source}')


class LTIExceptionBadParameterValue(LTIException):
    def __init__(self, reason):
        super().__init__(f'Bad parameter value: {reason}')


class LTIExceptionTooLittleData(LTIException):
    def __int__(self, reason):
        super().__int__(f'Too little data: {reason}')


class LTIExceptionBadDataCachFile:
    def __init__(self):
        super().__init__('Bad data cach file')