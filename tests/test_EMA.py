import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_ema(config_default, test_source, test_symbol, time_begin, time_end, period, a_timeframe):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    out = indicators.OHLCV(test_symbol, a_timeframe)
    ema = indicators.EMA(test_symbol, a_timeframe, period=period)

    source_values = out.close
    values_ema = ema.ema_close

    alpha = 1.0 / (period + 1)
    alpha_n = 1.0 - alpha
    ema_value = source_values[0]
    for i, value in enumerate(source_values):
        ema_value = value * alpha + ema_value * alpha_n
        assert round(values_ema[i], 8) == round(ema_value, 8)
