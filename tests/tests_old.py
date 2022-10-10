import unittest
import numpy as np
import __init__ as fti


class TestBasic(unittest.TestCase):

    def setUp(self) -> None:
        self.datasource_name = 'datasources.binance_ticks'
        self.symbol = 'um/btcusdt'
        self.timeframe = fti.Timeframe.t1h

    def test_no_date(self):
        indicators = fti.Indicators(self.datasource_name) #, date_begin=20200101, date_end=20200120)
        with self.assertRaises(fti.FTIException):
            indicators.OHLCV(self.symbol, self.timeframe)

    def test_no_date_end(self):
        indicators = fti.Indicators(self.datasource_name, date_begin=20200101)
        with self.assertRaises(fti.FTIException):
            indicators.OHLCV(self.symbol, self.timeframe)

    def test_no_date_begin(self):
        indicators = fti.Indicators(self.datasource_name, date_end=20200101)
        with self.assertRaises(fti.FTIException):
            indicators.OHLCV(self.symbol, self.timeframe)

    def test_OHLCV(self):
        indicators = fti.Indicators(self.datasource_name, date_begin=20200101, date_end=20200101)
        out = indicators.OHLCV(self.symbol, self.timeframe)


if __name__ == "__main__":

    test_suite = unittest.TestSuite()
    test_suite.addTest(TestBasic)
    print("count of tests: " + str(test_suite.countTestCases()) + "\n")

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
