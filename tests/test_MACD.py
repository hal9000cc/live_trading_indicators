import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


@pytest.mark.parametrize('time_begin, time_end, period_short, period_long, period_signal', [
    ('2022-07-01', '2022-07-10', 14, 21, 3),
    ('2022-07-01', '2022-07-10', 8, 14, 1)
])
def test_macd(config_default, test_source, test_symbol, time_begin, time_end,
              period_short, period_long, period_signal):

    timeframe = '1m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    macd = indicators.MACD(test_symbol, timeframe,
                           period_short=period_short, period_long=period_long,
                           period_signal=period_signal, ma_type_signal='ema')

    stoch_ref_macd = si.get_macd(ohlcv2quote(ohlcv), period_short, period_long, period_signal)

    ref_value_macd = stocks2numpy(stoch_ref_macd, 'macd')
    ref_value_hist = stocks2numpy(stoch_ref_macd, 'histogram')
    ref_value_signal = stocks2numpy(stoch_ref_macd, 'signal')

    assert (macd.macd[period_long + period_signal:] - ref_value_macd[period_long + period_signal:] < 1e-10).all()
    assert (macd.macd_signal[period_long + period_signal:] - ref_value_signal[period_long + period_signal:] < 1e-10).all()
    assert (macd.macd_hist[period_long*10:] - ref_value_hist[period_long*10:] < 1e-6).all()
