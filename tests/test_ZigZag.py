import pytest
from common_test import *
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, timeframe, delta', [
    ('2022-07-02', '2022-07-03', '1h', 0.02),
    ('2022-07-02', '2022-07-07', '1h', 0.01),
    ('2022-07-01', '2022-07-01', '1h', 0.01),
    ('2022-07-03', '2022-07-08', '1h', 0.01),
    ('2022-07-04', '2022-07-07', '1h', 0.01),
    ('2022-07-05', '2022-07-07', '1h', 0.01),
    ('2022-07-06', '2022-07-07', '1h', 0.01),
    ('2022-07-07', '2022-07-07', '1h', 0.01)
])
def test_zig_zag(config_default, test_source, a_symbol, time_begin, time_end, timeframe, delta):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(a_symbol, timeframe)
    zig_zag = indicators.ZigZag(a_symbol, timeframe, delta=delta, end_points=True)  # only pass
    zig_zag = indicators.ZigZag(a_symbol, timeframe, delta=delta)

    ref_values = get_ref_values('get_zig_zag', ohlcv, 'point_type, retrace_high, retrace_low, zig_zag', 'HIGH_LOW', delta * 100)

    ref_point_type = np.zeros(len(ref_values.point_type), dtype=np.int8)
    ref_point_type[ref_values.point_type == 'H'] = 1
    ref_point_type[ref_values.point_type == 'L'] = -1

    i_start_check = np.flatnonzero(zig_zag.pivot_types != 0)[2]

    #assert compare_with_nan(zig_zag.pivot_types[i_start_check:], ref_point_type[i_start_check:])
    (zig_zag.pivot_types[i_start_check:] != ref_point_type[i_start_check:]).sum() / len(zig_zag) < 0.02
 

@pytest.mark.parametrize('time_begin, time_end, timeframe, delta, depth, symbol', [
    ('2022-07-07', '2022-07-08', '1h', 0.02, 1, 'um/ethusdt'),
    ('2022-07-07', '2022-07-08', '1h', 0.02, 2, 'um/ethusdt'),
    ('2022-07-07', '2022-07-08', '1h', 0.02, 3, 'um/ethusdt'),
    ('2022-07-07', '2022-07-08', '1h', 0.02, 4, 'um/ethusdt'),
    ('2022-07-07', '2022-07-08', '1h', 0.02, 5, 'um/ethusdt'),
])
def test_zig_zag_paint(config_default, test_source, symbol, time_begin, time_end, timeframe, delta, depth):

    indicators = lti.Indicators(test_source, time_begin, time_end)

    zig_zag = indicators.ZigZag(symbol, timeframe, delta=delta, depth=depth)
    zig_zag.show()

    zig_zag = indicators.ZigZag(symbol, timeframe, delta=delta, depth=depth, end_points=True)
    zig_zag.show()
