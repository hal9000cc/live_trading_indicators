import src.fast_trading_indicators as fti
import pytest
import conftest


def test_bad_datasource():
    with pytest.raises(TypeError) as error:
        indicators = fti.Indicators(None)


def test_no_date(default_source, default_symbol):
    indicators = fti.Indicators(default_source)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, fti.Timeframe.t1h)
    assert error.value.message == 'No begin_date set'


def test_no_date_end(default_source, default_symbol):
    indicators = fti.Indicators(default_source, date_begin=20200101)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, fti.Timeframe.t1h)
    assert error.value.message == 'No end_date set'


def test_no_date_begin(default_source, default_symbol):
    indicators = fti.Indicators(default_source, date_end=20200101)
    with pytest.raises(fti.FTIException) as error:
        indicators.OHLCV(default_symbol, fti.Timeframe.t1h)
    assert error.value.message == 'No begin_date set'


def test_OHLCV_symbol_not_found(clear_data):
    indicators = fti.Indicators('binance_ticks', date_begin=20220201, date_end=20220201, common_data_path=clear_data)
    with pytest.raises(fti.FTIException) as error:
        out = indicators.OHLCV('cm/ethusd', fti.Timeframe.t1h)
    assert error.value.message == 'Symbol cm/ethusd not found in source binance_ticks.'


@pytest.mark.parametrize('source, symbol, date_begin, date_end', [
    ('binance_ticks', 'um/ethusdt', 20200201, 20200201),
    ('binance_ticks', 'um/ethusdt', 20200201, 20200202),
    ('binance_ticks', 'cm/ethusd_perp', 20200201, 20200202),
    ('binance_ticks', 'um/ethusdt', 20220930, 20220930),
    ('binance_ticks', 'ethusdt', 20220930, 20220930),
])
def test_OHLCV_clear_data(source, symbol, date_begin, date_end, clear_data):
    indicators = fti.Indicators(source, date_begin=date_begin, date_end=date_end, common_data_path=clear_data)
    out = indicators.OHLCV(symbol, fti.Timeframe.t1h)
    assert False


def test_OHLCV(default_source, default_symbol):
    indicators = fti.Indicators(default_source, date_begin=20200101, date_end=20200101)
    out = indicators.OHLCV(default_symbol, fti.Timeframe.t1h)
    assert False