import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, start, maximum, increment', [
    ('2022-07-01', '2022-07-10', 0.02, 0.2, 0.02),
    ('2022-07-02', '2022-07-10', 0.01, 0.2, 0.02),
    ('2022-07-03', '2022-07-10', 0.02, 0.3, 0.01),
    ('2022-07-04', '2022-07-10', 0.02, 0.2, 0.02),
    ('2022-07-05', '2022-07-10', 0.01, 0.2, 0.02),
    ('2022-07-06', '2022-07-10', 0.02, 0.3, 0.01)
])
def test_parabolic_SAR(config_default, test_source, test_symbol, time_begin, time_end, start, maximum, increment):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    sar = indicators.ParabolicSAR(test_symbol, timeframe, start=start, maximum=maximum, increment=increment)

    ref_values = get_ref_values('get_parabolic_sar', ohlcv, 'sar, is_reversal', increment, maximum, start)

    ref_values.is_reversal[np.isnan(ref_values.is_reversal)] = 0
    assert (abs(sar.signal) == ref_values.is_reversal).all()
    assert compare_with_nan(sar.sar, ref_values.sar)


