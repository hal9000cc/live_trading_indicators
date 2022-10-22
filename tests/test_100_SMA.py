import pytest
import src.fast_trading_indicators as fti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-22', 1),
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_sma(config_default, default_source, default_symbol, time_begin, time_end, period, a_timeframe):

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, a_timeframe, time_begin=time_begin, time_end=time_end)
    sma = indicators.SMA(default_symbol, a_timeframe, period, time_begin=time_begin, time_end=time_end)

    values = out.close
    values_sma = sma.value
    sum = 0
    n = 0
    for i in range(len(values)):

        sum += values[i]
        if n < period:
            n += 1
        else:
            sum -= values[i - period]

        assert round(values_sma[i], 8) == round(sum / n, 8)


@pytest.mark.parametrize('time_begin, time_end, period, timeframe', [
    ('2022-07-01', '2022-07-10', 22, fti.Timeframe.t1d),
    ('2022-07-01', '2022-07-21', 22, fti.Timeframe.t1d),
    ('2022-07-01', '2022-07-10', 241, fti.Timeframe.t1d),
    ('2022-07-01', '2022-07-10', 0, fti.Timeframe.t1d)
])
def test_sma_value_error(config_default, default_source, default_symbol, time_begin, time_end, period, timeframe):

    indicators = fti.Indicators(default_source)
    out = indicators.OHLCV(default_symbol, timeframe, time_begin=time_begin, time_end=time_end)
    with pytest.raises(ValueError):
        sma = indicators.SMA(default_symbol, timeframe, period, time_begin=time_begin, time_end=time_end)
