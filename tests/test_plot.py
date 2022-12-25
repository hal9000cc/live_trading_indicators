import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-03')
])
def test_plot(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)

    ohlcv.show()
    pass

