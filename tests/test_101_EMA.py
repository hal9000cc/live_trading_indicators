import pytest
import src.fast_trading_indicators as fti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_ema(config_default, default_source, default_symbol, time_begin, time_end, period, a_timeframe):

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, a_timeframe, time_begin=time_begin, time_end=time_end)
    ema = indicators.EMA(default_symbol, a_timeframe, period, time_begin=time_begin, time_end=time_end)

    source_values = out.close
    values_ema = ema.value

    alpha = 1.0 / (period + 1)
    alpha_n = 1.0 - alpha
    ema_value = source_values[0]
    for i, value in enumerate(source_values):
        ema_value = value * alpha + ema_value * alpha_n
        assert round(values_ema[i], 8) == round(ema_value, 8)
