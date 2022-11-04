# live_trading_indicators
# OHLCV(symbol, timeframe')

def get_indicator_out(indicators, symbols, timeframe, out_for_grow, **kwargs):

    return indicators.get_bar_data(symbols, timeframe, out_for_grow)

