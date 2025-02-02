import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period_short, period_long, period_signal', [
    ('2022-07-01', '2022-07-10', 2, 3, 1),
    ('2022-07-01', '2022-07-10', 2, 3, 2),
    ('2022-07-01', '2022-07-10', 14, 21, 3),
    ('2022-07-01', '2022-07-10', 8, 14, 1),
    ((dt.datetime.utcnow() - dt.timedelta(days=2)).date(), None, 8, 14, 2)  # live
])
def test_macd(config_default, test_source, test_symbol, time_begin, time_end,
              period_short, period_long, period_signal):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    macd = indicators.MACD(test_symbol, timeframe,
                           period_short=period_short, period_long=period_long,
                           period_signal=period_signal, ma_type_signal='ema')

    ref_values = get_ref_values('get_macd', ohlcv, 'macd, histogram, signal', period_short, period_long, period_signal)

    assert compare_with_nan(macd.macd, ref_values.macd)
    assert compare_with_nan(macd.signal, ref_values.signal)
    assert compare_with_nan(macd.hist, ref_values.histogram)
