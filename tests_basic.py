import numpy as np
import __init__ as fti
import datasources


def run(datasource_name, symbol, timeframe):
    indicators = fti.Indicators(datasource_name, timeframe_data_path='aaa')
    price_data = indicators.OHLCV(symbol, timeframe)
    ma_data = indicators.SMA(symbol, timeframe, 23)

if __name__ == '__main__':
    run('datasources.binance_ticks', 'um/btcusdt', fti.Timeframe.t1h)