import timeit

import pytest

import src.live_trading_indicators as lti


def test_benchmark():

    return

    symbol = 'ethusdt'
    timeframe = '1s'

    indicators = lti.Indicators('binance', '2021-01-01', '2021-12-31', max_empty_bars_fraction=0.02, max_empty_bars_consecutive=-1)

    test_globals = {'indicators': indicators, 'symbol': symbol, 'timeframe': timeframe}

    time = timeit.timeit('print(indicators.OHLCV(symbol, timeframe))', number=1, globals=test_globals)
    print(f'Load OHLCV: {time} seconds\n')

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

    test_globals['indicator_params'] = indicator_params

    for indicator_name in lti.indicators_list():
        if indicator_name in ('VolumeClusters', 'OHLCVM'):
            continue

        test_globals['indicator_name'] = indicator_name
        time = timeit.timeit(
            'indicator = indicators.get_indicator(indicator_name)\n'
            'params = indicator_params.get(indicator_name, {})\n'
            'print(indicator(symbol, timeframe, **params))',
                             number=1, globals=test_globals)
        print(f'{indicator_name}: {time} seconds\n')
