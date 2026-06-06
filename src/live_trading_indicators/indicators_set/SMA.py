"""SMA(period=, value='close')
Simple moving average."""
from ..move_average import ma_calculate, MA_Type
from ..indicator_data import IndicatorData

OUTPUT_SERIES = (
    {'name': 'sma', 'type': 'as_source', 'range': 'as_source'},
)


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period, value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    out = ma_calculate(source_values, period, MA_Type.sma)

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period': period, 'value': value},
        'name': 'SMA',
        'output_series': OUTPUT_SERIES,
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'sma': out,
        'allowed_nan': True
    })

