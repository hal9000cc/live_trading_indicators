import numpy as np
import numba as nb
from .constants import PRICE_TYPE


@nb.njit
def ema_calculate(source_values, alpha):

    alpha_n = 1.0 - alpha

    result = np.zeros(len(source_values), dtype=PRICE_TYPE)

    ema_value = source_values[0]
    for i, value in enumerate(source_values):
        ema_value = value * alpha + ema_value * alpha_n
        result[i] = ema_value

    return result


def ma_calculate(source_values, period):

    if period == 1:
        return source_values

    data_len = len(source_values)
    if data_len < period:
        raise ValueError(f'Period SMA more then data size ({data_len} < {period})')

    weights = np.ones(period, dtype=source_values.dtype) / period

    out = np.convolve(source_values, weights)[:-period+1]
    begin_multiple = period / np.arange(1, period, dtype=float)
    out[:period - 1] *= begin_multiple

    return out

