import importlib
import numbers

import numpy as np

import live_trading_indicators as lti
from live_trading_indicators.indicator_data import IndicatorData
from live_trading_indicators.timeframe import Timeframe


INDICATOR_MODULES = {
    'ADL', 'ADX', 'ATR', 'Aroon', 'Awesome', 'BollingerBands', 'CCI', 'Chandelier', 'EMA', 'Ichimoku', 'Keltner',
    'MA', 'MACD', 'MFI', 'OBV', 'OHLCVM', 'ParabolicSAR', 'ROC', 'RSI', 'SMA', 'Stochastic', 'Supertrend', 'TEMA',
    'TRIX', 'VWAP', 'VWMA', 'VolumeClusters', 'VolumeOsc', 'WilliamsR', 'ZigZag'
}


def test_output_series_constants_format():
    for module_name in INDICATOR_MODULES:
        module = importlib.import_module(f'live_trading_indicators.indicators_set.{module_name}')
        assert hasattr(module, 'OUTPUT_SERIES')
        assert isinstance(module.OUTPUT_SERIES, tuple)
        assert len(module.OUTPUT_SERIES) > 0

        for series in module.OUTPUT_SERIES:
            assert set(series.keys()) == {'name', 'type', 'range'}
            assert isinstance(series['name'], str)
            assert series['type'] in ('price', 'as_source', 'none')
            assert series['range'] is None or series['range'] == 'as_source' or isinstance(series['range'], dict)

            if isinstance(series['range'], dict):
                assert set(series['range'].keys()) == {'min', 'max'}
                assert isinstance(series['range']['min'], numbers.Real)
                assert isinstance(series['range']['max'], numbers.Real)
                assert series['range']['min'] <= series['range']['max']


def test_selected_output_series_metadata():
    bb = importlib.import_module('live_trading_indicators.indicators_set.BollingerBands')
    rsi = importlib.import_module('live_trading_indicators.indicators_set.RSI')
    sma = importlib.import_module('live_trading_indicators.indicators_set.SMA')

    assert bb.OUTPUT_SERIES == (
        {'name': 'mid_line', 'type': 'price', 'range': None},
        {'name': 'up_line', 'type': 'price', 'range': None},
        {'name': 'down_line', 'type': 'price', 'range': None},
        {'name': 'z_score', 'type': 'none', 'range': None},
    )
    assert rsi.OUTPUT_SERIES == ({'name': 'rsi', 'type': 'none', 'range': {'min': 0, 'max': 100}},)
    assert sma.OUTPUT_SERIES == ({'name': 'sma', 'type': 'as_source', 'range': 'as_source'},)


def test_indicator_data_output_series_and_slice():
    class DummyIndicators:
        datasource_id = 'test'

    output_series = ({'name': 'value', 'type': 'price', 'range': None},)
    indicator_data = IndicatorData({
        'indicators': DummyIndicators(),
        'name': 'TestIndicator',
        'output_series': output_series,
        'symbol': 'test',
        'timeframe': Timeframe.t1m,
        'time': np.array(['2024-01-01T00:00', '2024-01-01T00:01'], dtype='datetime64[s]'),
        'value': np.array([1.0, 2.0]),
    })

    assert indicator_data.output_series == output_series
    assert indicator_data[:1].output_series == output_series


def test_indicator_result_contains_output_series(config_default, test_source, test_symbol):
    indicators = lti.Indicators(test_source, '2022-07-01', '2022-07-10', **config_default)
    bollinger_bands = indicators.BollingerBands(test_symbol, Timeframe.t5m, period=20, deviation=2)

    assert bollinger_bands.output_series == (
        {'name': 'mid_line', 'type': 'price', 'range': None},
        {'name': 'up_line', 'type': 'price', 'range': None},
        {'name': 'down_line', 'type': 'price', 'range': None},
        {'name': 'z_score', 'type': 'none', 'range': None},
    )
    assert bollinger_bands[:10].output_series == bollinger_bands.output_series