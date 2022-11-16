import pytest
from common_test import *
import src.live_trading_indicators as lti
from stock_indicators import indicators as si


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

    bb_ref = si.get_bollinger_bands(ohlcv2quote(ohlcv), period, deviation)

    ref_value_mid = stocks2numpy(bb_ref, 'sma')
    ref_value_up = stocks2numpy(bb_ref, 'upper_band')
    ref_value_down = stocks2numpy(bb_ref, 'lower_band')
    ref_z_score = stocks2numpy(bb_ref, 'z_score')

    ref_z_score[np.isnan(ref_z_score)] = 0
    assert (bollinger_bands.mid_line[period - 1:] - ref_value_mid[period - 1:] < 1e-12).all()
    assert (bollinger_bands.up_line[period - 1:] - ref_value_up[period - 1:] < 1e-12).all()
    assert (bollinger_bands.down_line[period - 1:] - ref_value_down[period - 1:] < 1e-12).all()
    assert (bollinger_bands.z_score[period - 1:] - ref_z_score[period - 1:] < 1e-11).all()

