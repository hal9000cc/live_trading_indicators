import pytest
import src.fast_trading_indicators as fti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_rsi(config_default, default_source, default_symbol, time_begin, time_end, period, a_timeframe):

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, a_timeframe, time_begin=time_begin, time_end=time_end)
    rsi = indicators.RSI(default_symbol, a_timeframe, period, time_begin=time_begin, time_end=time_end)

    # need check values!