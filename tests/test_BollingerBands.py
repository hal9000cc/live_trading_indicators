import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period, deviation', [
    ('2022-07-01', '2022-07-10', 2, 1),
    ('2022-07-01', '2022-07-10', 2, 2),
    ('2022-07-01', '2022-07-10', 20, 1),
    ('2022-07-01', '2022-07-10', 20, 3)
])
def test_bollinger_bands(config_default, test_source, test_symbol, time_begin, time_end, period, deviation):

    timeframe = '5m'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    bollinger_bands = indicators.BollingerBands(test_symbol, timeframe, period=period, deviation=deviation)

    ref_values = get_ref_values('bollinger_bands', ohlcv, 'sma, upper_band, lower_band, z_score', period, deviation)

    assert compare_with_nan(bollinger_bands.mid_line, ref_values.sma)
    assert compare_with_nan(bollinger_bands.up_line, ref_values.upper_band)
    assert compare_with_nan(bollinger_bands.down_line, ref_values.lower_band)
    assert compare_with_nan(bollinger_bands.z_score, ref_values.z_score)

