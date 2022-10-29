import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end, period_K, period_D, slowing, ma_method', [
    ('2022-07-01', '2022-07-10', 21, 8, 3, 'sma'),
    ('2022-07-01', '2022-07-10', 8, 21, 1, 'ema')
])
@pytest.mark.skip('in develop')
def test_stochastic(config_default, test_source, test_symbol, time_begin, time_end,
             period_K, period_D, slowing, ma_method, a_timeframe):

    indicators = lti.Indicators(test_source, time_begin, time_end)
    out = indicators.OHLCV(test_symbol, a_timeframe)
    stochastic = indicators.Stockhastic(test_symbol, a_timeframe,
                                        period_K=period_K, period_D=period_D, slowing=slowing, ma_method=ma_method)

    # need check values!