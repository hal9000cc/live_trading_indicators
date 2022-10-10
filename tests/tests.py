import __init__ as fti
import pytest


def test_no_date():
    indicators = fti.Indicators(self.datasource_name)
    with pytest.raises(fti.FTIException):
        indicators.OHLCV(self.symbol, self.timeframe)


def test_no_date_end(self):
    indicators = fti.Indicators(self.datasource_name, date_begin=20200101)
    with pytest.raises(fti.FTIException):
        indicators.OHLCV(self.symbol, self.timeframe)

def test_no_date_begin(self):
    indicators = fti.Indicators(self.datasource_name, date_end=20200101)
    with pytest.raises(fti.FTIException):
        indicators.OHLCV(self.symbol, self.timeframe)


def test_OHLCV(self):
    indicators = fti.Indicators(self.datasource_name, date_begin=20200101, date_end=20200101)
    out = indicators.OHLCV(self.symbol, self.timeframe)
    assert False
