import os
import numpy as np
import os.path as path
import datetime as dt
import src.live_trading_indicators as lti
import pytest
from src.live_trading_indicators.common import HOME_FOLDER, param_time
from memory_profiler import memory_usage
import importlib


@pytest.mark.parametrize('source, symbol, date_begin, date_end, control_values', [
    ('binance', 'um/ethusdt', 20200201, 20200201,
        ([180.14, 181.36, 184.00, 184.09], [181.73, 184.10, 184.58, 184.26], [179.41, 181.31, 182.93, 182.92],
        [181.36, 184.00, 184.10, 183.79], [19477.981, 31579.898, 30595.211, 17646.828])),
    ('binance', 'um/ethusdt', 20200201, 20200202, None),
    ('binance', 'cm/ethusd_perp', 20220201, 20220201, None),
    ('binance', 'um/ethusdt', 20220930, 20220930, None),
    ('binance', 'ethusdt', 20220930, 20220930, None),
])
def test_OHLCV_clear_data(config_clear_data_t, config_clear_data_a, source, symbol, date_begin, date_end, control_values):

    for config in (config_clear_data_t, config_clear_data_a):

        indicators = lti.Indicators(source, date_begin=date_begin, date_end=date_end, **config)

        out = indicators.OHLCV(symbol, lti.Timeframe.t1h)
        if control_values:
            assert (out.open[:4] == control_values[0]).all()
            assert (out.high[:4] == control_values[1]).all()
            assert (out.low[:4] == control_values[2]).all()
            assert (out.close[:4] == control_values[3]).all()
            assert (out.volume[:4] == control_values[4]).all()


@pytest.mark.parametrize('source, symbol, date_begin, date_end', [
    ('binance', 'um/ethusdt', 20200201, 20200201),
    ('binance', 'um/ethusdt', 20200201, 20200202),
    ('binance', 'cm/ethusd_perp', 20220201, 20220201),
    ('binance', 'um/ethusdt', 20220930, 20220930),
    ('binance', 'ethusdt', 20220930, 20220930),
])
@pytest.mark.skip
def test_compare_full_and_agg_ticks(config_clear_data_t, config_clear_data_a, source, symbol, date_begin, date_end):

    timeframe = lti.Timeframe.t1h

    indicators = lti.Indicators(source, date_begin=date_begin, date_end=date_end, **config_clear_data_t)
    out_full = indicators.OHLCV(symbol, timeframe)

    d_begin, date_end = param_time(date_begin, False).date(), param_time(date_end, True).date()
    date_of_file = d_begin
    while date_of_file <= date_end:
        lti_filename = indicators.source_data.filename_day_data(symbol, timeframe, date_of_file)
        os.remove(lti_filename)
        date_of_file += dt.timedelta(days=1)

    indicators = lti.Indicators(source, date_begin=date_begin, date_end=date_end, **config_clear_data_a)
    out_agg = indicators.OHLCV(symbol, lti.Timeframe.t1h)

    assert (out_full.time == out_agg.time).all()
    assert (out_full.open == out_agg.open).all()
    assert (out_full.high == out_agg.high).all()
    assert (out_full.low == out_agg.low).all()
    assert (out_full.close == out_agg.close).all()
    assert (out_full.volume == out_agg.volume).all()


def test_memory_leak_tickd_downlad(config_clear_data_t, test_source, test_symbol):

    mu_begin = memory_usage()[0]

    sources_folder = path.join(HOME_FOLDER, 'data', 'sources')
    config_clear_data_t[sources_folder] = sources_folder
    indicators = lti.Indicators(test_source, date_begin=20220901, date_end=20220902, **config_clear_data_t)

    out = indicators.OHLCV(test_symbol, lti.Timeframe.t1h)
    assert memory_usage()[0] - mu_begin < 100


@pytest.mark.parametrize('source, symbol, date_begin, date_end', [
    ('binance', 'um/ethusdt', 20200201, 20200201),
    ('binance', 'um/ethusdt', 20220910, 20220910),
    ('binance', 'cm/ethusd_perp', 20220201, 20220201),
    ('binance', 'um/ethusdt', 20220930, 20220930),
    ('binance', 'ethusdt', 20220930, 20220930),
])
def test_OHLCV_bars(config_clear_data_t, source, symbol, date_begin, date_end):

    timeframe = lti.Timeframe.t1h

    indicators = lti.Indicators(source, date_begin=date_begin, date_end=date_end, **config_clear_data_t)

    out_using_ticks = indicators.OHLCV(symbol, timeframe)

    source_module = importlib.import_module(f'src.live_trading_indicators.datasources.{source}', __package__)
    source_module.init(lti.config())
    out_using_bars = source_module.bars_of_day_from_klines(symbol, timeframe, param_time(date_begin, False).date())

    assert (out_using_ticks.time == out_using_bars.time).all()
    assert (out_using_ticks.open == out_using_bars.open).all()
    assert (out_using_ticks.high == out_using_bars.high).all()
    assert (out_using_ticks.low == out_using_bars.low).all()
    assert (out_using_ticks.close == out_using_bars.close).all()
    assert (out_using_ticks.volume == out_using_bars.volume).all()


@pytest.mark.parametrize('source, timeframe, date_begin, date_end', [
    ('binance', lti.Timeframe.t1h, 20220901, 20220901)])
@pytest.mark.skip
def test_OHLCV_agg_ticks_all_symbols(config_default_a, source, timeframe, date_begin, date_end, all_symbols):

    indicators = lti.Indicators(source, date_begin=date_begin, date_end=date_end, **config_default_a)

    out_using_ticks = indicators.OHLCV(all_symbols, timeframe)
    # try:
    #     out_using_ticks = indicators.OHLCV(all_symbols, timeframe)
    # except lti.LTISourceDataNotFound:
    #     return
    # except lti.LTIExceptionTooManyEmptyBars:
    #     return

    source_module = importlib.import_module(f'src.live_trading_indicators.datasources.{source}', __package__)
    source_module.init(lti.config())
    out_using_bars = source_module.bars_of_day_from_klines(all_symbols, timeframe, param_time(date_begin, False).date())

    assert (out_using_ticks.time == out_using_bars.time).all()
    assert (out_using_ticks.open == out_using_bars.open).all()
    assert (out_using_ticks.high == out_using_bars.high).all()
    assert (out_using_ticks.low == out_using_bars.low).all()
    assert (out_using_ticks.close == out_using_bars.close).all()
    assert (out_using_ticks.volume == out_using_bars.volume).all()


@pytest.mark.parametrize('source, timeframe, date_begin, date_end', [
    ('binance', lti.Timeframe.t1h, 20220901, 20220901)])
def test_OHLCV_full_ticks_all_symbols(config_clear_data_t, source, timeframe, date_begin, date_end, all_symbols):

    indicators = lti.Indicators(source, date_begin, date_end, **config_clear_data_t)

    out_using_ticks = indicators.OHLCV(all_symbols, timeframe)
    # try:
    #     out_using_ticks = indicators.OHLCV(all_symbols, timeframe)
    # except lti.LTISourceDataNotFound:
    #     return
    # except lti.LTIExceptionTooManyEmptyBars:
    #     return

    source_module = importlib.import_module(f'src.live_trading_indicators.datasources.{source}', __package__)
    source_module.init(lti.config())
    out_using_bars = source_module.bars_of_day_from_klines(all_symbols, timeframe, param_time(date_begin, False).date())

    assert (out_using_ticks.time == out_using_bars.time).all()
    assert (out_using_ticks.open == out_using_bars.open).all()
    assert (out_using_ticks.high == out_using_bars.high).all()
    assert (out_using_ticks.low == out_using_bars.low).all()
    assert (out_using_ticks.close == out_using_bars.close).all()
    assert (out_using_ticks.volume == out_using_bars.volume).all()
