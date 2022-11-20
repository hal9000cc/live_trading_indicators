import pytest
from common_test import *
import src.live_trading_indicators as lti
from src.live_trading_indicators.cast_input_params import cast_time


def test_offline_source(config_default, test_source, ohlcv_set):

    symbol = ohlcv_set[0]
    timeframe = ohlcv_set[1]
    time_begin = cast_time(ohlcv_set[2])
    dataframe = ohlcv_set[4]
    dataframe.rename(columns={'open_time': 'time'}, inplace=True)

    if 'open' not in set(dataframe.columns):
        dataframe.rename(columns={0: 'time', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume', }, inplace=True)

    indicators_online = lti.Indicators(test_source)
    indicators_offline = lti.Indicators(dataframe)

    ohlcv_offline = indicators_offline.OHLCV()
    time_begin, time_end = ohlcv_offline.time[0], ohlcv_offline.time[-1]
    ohlcv_online = indicators_online.OHLCV(symbol, timeframe, time_begin, time_end)

    assert ohlcv_online == ohlcv_offline

    time_begin += np.timedelta64(1, 'h')
    time_end -= np.timedelta64(1, 'h')
    ohlcv_offline = indicators_offline.OHLCV(time_begin, time_end)
    ohlcv_online = indicators_online.OHLCV(symbol, timeframe, time_begin, time_end)

    assert ohlcv_online == ohlcv_offline

    if len(ohlcv_offline) > 60:
        macd = indicators_offline.MACD(period_short=15, period_long=26, period_signal=9)
        print(macd[50:].pandas().head())
