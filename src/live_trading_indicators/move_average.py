import numpy as np
from numba import njit
from enum import Enum
from .constants import PRICE_TYPE
from .exceptions import *


class MA_Type(Enum):

    ema = 1
    sma = 2
    mma = 3
    ema0 = 4
    mma0 = 5

    @staticmethod
    def cast(str_value):

        match str_value.lower():
            case 'ema':
                return MA_Type.ema
            case 'sma':
                return MA_Type.sma
            case 'mma':
                return MA_Type.mma
            case 'ema0':
                return MA_Type.ema0
            case 'mma0':
                return MA_Type.mma0

        raise ValueError(f'Unknown move average type: {str_value}')


@njit(cache=True)
def get_first_index_not_nan(values):

    for i, value in enumerate(values):
        if not np.isnan(values[i]):
            return i

    return len(values)


@njit(cache=True)
def ema_calculate(source_values, alpha, first_value=np.nan, start=0):

    alpha_n = 1.0 - alpha

    if np.isnan(first_value):
        # skip first nans
        for i, value in enumerate(source_values):
            ema_value = source_values[i]
            if not np.isnan(ema_value):
                start = i
                break
        else:
            ema_value = source_values[start]
    else:
        ema_value = first_value

    result = np.empty(len(source_values), dtype=float)
    result[: start] = np.nan
    result[start] = ema_value

    for i in range(start + 1, len(source_values)):
        ema_value = source_values[i] * alpha + ema_value * alpha_n
        result[i] = ema_value

    return result


def sma_calculate(source_values, period):

    if period == 1:
        return source_values

    data_len = len(source_values)
    if data_len < period:
        raise LTIExceptionTooLittleData(f'data length {data_len} < {period}')

    weights = np.ones(period, dtype=source_values.dtype) / period

    out = np.convolve(source_values, weights)[:-period+1]
    out[:period - 1] = np.nan

    return out


def iema_calculate(source_values, period, alpha):

    start = get_first_index_not_nan(source_values)

    data_len = len(source_values)
    if data_len < start + period:
        raise LTIExceptionTooLittleData(f'data length {data_len} < {start + period}')

    first_value = source_values[start: start + period].sum() / period
    return ema_calculate(source_values, alpha, first_value, start + period - 1)


def ma_calculate(source_values, period, ma_type):

    match ma_type:
        case MA_Type.sma:
            return sma_calculate(source_values, period)
        case MA_Type.ema0:
            alpha = 2.0 / (period + 1)
            return ema_calculate(source_values, alpha)
        case MA_Type.mma0:
            alpha = 1.0 / period
            return ema_calculate(source_values, alpha)
        case MA_Type.ema:
            alpha = 2.0 / (period + 1)
            return iema_calculate(source_values, period, alpha)
        case MA_Type.mma:
            alpha = 1.0 / period
            return iema_calculate(source_values, period, alpha)

    raise ValueError(f'Bad ma_type value: {ma_type}')

