import numpy as np
import numba as nb
from .common import PRICE_TYPE


@nb.njit
def ema_calculate(source_values, alpha):

    alpha_n = 1.0 - alpha

    result = np.zeros(len(source_values), dtype=PRICE_TYPE)

    ema_value = source_values[0]
    for i, value in enumerate(source_values):
        ema_value = value * alpha + ema_value * alpha_n
        result[i] = ema_value

    return result
