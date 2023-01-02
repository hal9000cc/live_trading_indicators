import pytest
from common_test import *
import src.live_trading_indicators as lti
from src.live_trading_indicators import Timeframe


@pytest.mark.parametrize('time_begin, time_end, period, deviation, timeframe', [
    ('2022-07-01', '2022-07-10', 2, 1, Timeframe.t5m),
    ('2022-07-01', '2022-07-10', 2, 2, Timeframe.t5m),
    ('2022-07-01', '2022-07-10', 20, 1, Timeframe.t5m),
    ('2022-07-01', '2022-07-10', 20, 3, Timeframe.t5m),
    ('2022-07-01', '2022-07-05', 4, 2, Timeframe.t1h)
])
def test_bollinger_bands(config_default, test_source, test_symbol, time_begin, time_end, period, deviation, timeframe):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)
    bollinger_bands = indicators.BollingerBands(test_symbol, timeframe, period=period, deviation=deviation)

    ref_values = get_ref_values('get_bollinger_bands', ohlcv, 'sma, upper_band, lower_band, z_score', period, deviation)

    assert compare_with_nan(bollinger_bands.mid_line, ref_values.sma)
    assert compare_with_nan(bollinger_bands.up_line, ref_values.upper_band)
    assert compare_with_nan(bollinger_bands.down_line, ref_values.lower_band)
    assert compare_with_nan(bollinger_bands.z_score, ref_values.z_score)

    if timeframe.value >= Timeframe.t1h.value:
        bollinger_bands.show()


@pytest.mark.parametrize('time_begin, time_end, sma_period', [
    ('2022-07-01', '2022-07-07', 2)
])
def test_test_bollinger_bands_plot(config_default, test_source, time_begin, time_end, sma_period):

    symbol = 'um/ethusdt'
    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end, **config_default)
    bollinger_bands = indicators.BollingerBands(symbol, timeframe, period=14, deviation=2)

    bollinger_bands.show()
