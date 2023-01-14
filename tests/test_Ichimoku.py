import pytest
from common_test import *
import src.live_trading_indicators as lti
from src.live_trading_indicators import Timeframe
import datetime as dt

now = dt.datetime.utcnow()

@pytest.mark.parametrize('time_begin, time_end, timeframe, period_short, period_mid, period_long, offset_senkou, offset_chikou', [
    ('2022-07-01', '2023-01-13', Timeframe.t1d, 9, 26, 52, 26, 26),
    ('2022-07-01', '2023-01-13', Timeframe.t1d, 9, 26, 52, 25, 27),
    (now - dt.timedelta(days=100), now - dt.timedelta(days=1), Timeframe.t1d, 9, 26, 52, 25, 27)
])
def test_ichimoku(config_default, test_source, test_symbol, timeframe, time_begin, time_end,
                  period_short, period_mid, period_long, offset_senkou, offset_chikou):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    ichemoku = indicators.Ichimoku(test_symbol, timeframe, period_short=period_short, period_mid=period_mid,
                                   period_long=period_long, offset_senkou=offset_senkou, offset_chikou=offset_chikou)

    ref_values = get_ref_values('get_ichimoku', ohlcv, 'tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span',
                                period_short, period_mid, period_long, offset_senkou, offset_chikou)

    assert compare_with_nan(ichemoku.tenkan, ref_values.tenkan_sen)
    assert compare_with_nan(ichemoku.kijun, ref_values.kijun_sen)
    assert compare_with_nan(ichemoku.senkou_a, ref_values.senkou_span_a)
    assert compare_with_nan(ichemoku.senkou_b, ref_values.senkou_span_b)
    assert compare_with_nan(ichemoku.chikou, ref_values.chikou_span)


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2023-01-13')
])
def test_ichimoku_plot(config_default, test_source, time_begin, time_end):

    symbol = 'um/ethusdt'
    timeframe = '1d'

    indicators = lti.Indicators(test_source, time_begin, time_end, **config_default)
    ichimoku = indicators.Ichimoku(symbol, timeframe)

    ichimoku.show()
    pass