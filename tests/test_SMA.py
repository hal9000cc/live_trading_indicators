import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period', [
    ('2022-07-01', '2022-07-22', 1),
    ('2022-07-01', '2022-07-10', 3),
    ('2022-07-01', '2022-07-10', 5),
    ('2022-07-01', '2022-07-31', 22),
    ('2022-07-01', '2022-07-22', 22)
])
def test_sma(config_default, test_source, test_symbol, time_begin, time_end, period, a_timeframe):

    test_symbol = 'um/ethusdt'

    indicators = lti.Indicators(test_source)
    out = indicators.OHLCV(test_symbol, a_timeframe, time_begin, time_end)
    sma = indicators.SMA(test_symbol, a_timeframe, time_begin, time_end, period=period)

    values = out.close
    values_sma = sma.sma_close
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
    ('2022-07-01', '2022-07-10', 22, lti.Timeframe.t1d),
    ('2022-07-01', '2022-07-21', 22, lti.Timeframe.t1d),
    ('2022-07-01', '2022-07-10', 241, lti.Timeframe.t1d),
    ('2022-07-01', '2022-07-10', 0, lti.Timeframe.t1d)
])
def test_sma_value_error(config_default, test_source, time_begin, time_end, period, timeframe):

    symbol = 'btcusdt'

    indicators = lti.Indicators(test_source)
    out = indicators.OHLCV(symbol, timeframe, time_begin, time_end)
    with pytest.raises(ValueError):
        sma = indicators.SMA(symbol, timeframe, time_begin, time_end, period=period)