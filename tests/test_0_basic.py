import pytest
import src.fast_trading_indicators as fti
from src.fast_trading_indicators.common import date_from_arg, HOME_FOLDER


def test_bad_datasource(config_default):
    with pytest.raises(TypeError) as error:
        indicators = fti.Indicators(None)


def test_no_date(config_default, default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, default_timeframe)
    assert error.value.message == 'No begin_date set'


def test_no_date_end(config_default, default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source, date_begin=20200101)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, default_timeframe)
    assert error.value.message == 'No end_date set'


def test_no_date_begin(config_default, default_source, default_symbol, default_timeframe):
    indicators = fti.Indicators(default_source, date_end=20200101)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, default_timeframe)
    assert error.value.message == 'No begin_date set'


def test_OHLCV_symbol_not_found(config_default, default_timeframe):
    indicators = fti.Indicators('binance', date_begin=20220201, date_end=20220201)
    with pytest.raises(fti.FTIException) as error:
        out = indicators.OHLCV('cm/ethusd', default_timeframe)
    assert error.value.message == 'Symbol cm/ethusd not found in source binance.'


def test_OHLCV_ticks_not_found(config_default, default_timeframe):

    indicators = fti.Indicators('binance', date_begin=20100201, date_end=20100201)

    for symbol in ('um/ethusdt', 'cm/ethusd_perp', 'ethusdt'):
        with pytest.raises(fti.FTISourceDataNotFound) as error:
            out = indicators.OHLCV(symbol, default_timeframe)

