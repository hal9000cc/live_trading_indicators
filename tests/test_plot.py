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


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-03')
])
def test_plot_all(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '1h'

    indicator_params = {
        'CCI': {'period': 5},
        'EMA': {'period': 5},
        'MA': {'period': 5},
        'SMA': {'period': 5},
        'MACD': {'period_short': 5, 'period_long': 9, 'period_signal': 3},
        'RSI': {'period': 5},
        'Stochastic': {'period': 5, 'period_d': 9},
        'TEMA': {'period': 5},
        'TRIX': {'period': 5},
        'VWMA': {'period': 5}
    }

    indicators = lti.Indicators(test_source, time_begin, time_end)
    for indicator_name in lti.indicators_list():
        indicator = indicators.get_indicator(indicator_name)
        params = indicator_params.get(indicator_name, {})
        out = indicator(test_symbol, timeframe, **params)
        out.show()
