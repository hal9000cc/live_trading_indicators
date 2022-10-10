
def get_indicator_out(indicators, symbol, timeframe, *args, **kwargs):

    return indicators.timeframe_data_cash.get_timeframe_data(symbol, timeframe, indicators.date_begin, indicators.date_end)

