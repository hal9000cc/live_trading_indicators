"""BollingerBands(period=20, deviation=2, ma_type='sma', value='close')
Bollinger bands."""
import numpy as np
import numba as nb
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


@nb.njit(cache=True)
def calc_std_deviations(values, period):

    values_len = len(values)

    result = np.empty(values_len)
    result[:period - 1] = np.nan
    for i in range(period, values_len + 1):
        result[i - 1] = values[i - period: i].std()

    return result


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period=20, deviation=2, ma_type='sma', value='close'):

    # check_input_parameter(period > 1, period, 'period must be greater than 1')
    # check_input_parameter(name_is_ohlc(value), value)

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    mid_line = ma_calculate(source_values, period, MA_Type.cast(ma_type))

    std_deviations = calc_std_deviations(source_values, period)
    deviations = std_deviations * deviation

    up_line = mid_line + deviations
    down_line = mid_line - deviations

    z_score = (source_values - mid_line) / std_deviations

    return IndicatorData({
        'name': 'BollingerBands',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'mid_line': mid_line,
        'up_line': up_line,
        'down_line': down_line,
        'z_score': z_score,
        'allowed_nan': True
    })

