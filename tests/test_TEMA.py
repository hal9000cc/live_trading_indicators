import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 1),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-10', 22),
    ('2022-07-01', '2022-07-10', 14),
    ((dt.datetime.utcnow() - dt.timedelta(days=1)).date(), None, 14)  # live
])
def test_tema(config_default, test_source, test_symbol, time_begin, time_end, period):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    tema = indicators.TEMA(test_symbol, timeframe, period=period)

    ref_values = get_ref_values('get_tema', ohlcv, 'tema', period)

    assert compare_with_nan(tema.tema, ref_values.tema)
