"""VolumeOsc(period_long=5, period_short=10, ma_type='ema')
Volume oscillator."""
from ..move_average import ma_calculate, MA_Type
from ..indicator_data import IndicatorData


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period_short=5, period_long=10, ma_type='ema'):

    ma_type_enum = MA_Type.cast(ma_type)

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)

    vol_short = ma_calculate(ohlcv.volume, period_short, ma_type_enum)
    vol_long = ma_calculate(ohlcv.volume, period_long, ma_type_enum)
    osc = (vol_short - vol_long) / vol_long * 100

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period_short': period_short, 'period_long': period_long, 'ma_type': ma_type},
        'name': 'VolumeOsc',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'osc': osc,
        'allowed_nan': True
    })

