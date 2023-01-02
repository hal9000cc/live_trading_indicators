import pytest
import src.live_trading_indicators as lti


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-06')
])
def test_plot(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcv = indicators.OHLCV(test_symbol, timeframe)

    ohlcv.show()


@pytest.mark.parametrize('time_begin, time_begin_plot, time_end', [
    ('2022-07-01', '2022-07-03', '2022-07-09')
])
def test_plot_all(config_default, test_source, test_symbol, time_begin, time_begin_plot, time_end):

    timeframe = '1h'

    indicator_params = {
        'CCI': {'period': 14},
        'EMA': {'period': 14},
        'MA': {'period': 21},
        'SMA': {'period': 14},
        'MACD': {'period_short': 12, 'period_long': 26, 'period_signal': 9},
        'RSI': {'period': 14},
        'TEMA': {'period': 21},
        'TRIX': {'period': 13},
        'VWMA': {'period': 14}
    }

    indicators = lti.Indicators(test_source, time_begin, time_end)
    for indicator_name in lti.indicators_list():
        if indicator_name == 'VolumeClusters':
            continue
        indicator = indicators.get_indicator(indicator_name)
        params = indicator_params.get(indicator_name, {})
        out = indicator(test_symbol, timeframe, time_begin_plot, time_end, **params)
        out.show()
