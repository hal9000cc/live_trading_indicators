
def get_indicator_out(indicators, symbol, timeframe):

    return indicators.get_bar_data(symbol, timeframe, indicators.date_begin, indicators.date_end)

