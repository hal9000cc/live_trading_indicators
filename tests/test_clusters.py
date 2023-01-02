import pytest
from common_test import *
import src.live_trading_indicators as lti
from src.live_trading_indicators.timeframe import Timeframe


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-05')
])
def test_clusters(config_default, test_source, a_symbol, time_begin, time_end):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcvm = indicators.OHLCVM(a_symbol, timeframe)
    clusters = indicators.VolumeClusters(a_symbol, timeframe)
    ohlcv_low = indicators.OHLCV(a_symbol, '1m')

    multiplier = int(Timeframe.cast(timeframe).value // Timeframe.cast('1m'))

    for i in range(len(ohlcvm)):

        bars_low = ohlcv_low[i * multiplier: i * multiplier + multiplier]

        assert (bars_low.volume.sum() - ohlcvm.volume[i] < 1e-7).all()
        assert ohlcvm.low[i] <= ohlcvm.mv_price[i] <= ohlcvm.high[i]
        assert clusters.clusters_volume[i].sum() - ohlcvm.volume[i] < 1e-6

        hist, prices = np.histogram(np.hstack((bars_low.high, bars_low.low, bars_low.close)), bins=12,
                     weights=np.hstack((bars_low.volume / 3, bars_low.volume / 3, bars_low.volume / 3)))

        assert bars_low.low.min() == bars_low.high.max() or (prices == clusters.clusters_price[i]).all()
        assert (hist - clusters.clusters_volume[i] < 1e-9).all()

        i_mv = hist.argmax()
        mv_price = bars_low.low.min() if bars_low.low.min() == bars_low.high.max() else (prices[i_mv] + prices[i_mv + 1]) / 2
        assert mv_price == ohlcvm.mv_price[i]


@pytest.mark.parametrize('time_begin, time_end', [
    ('2022-07-01', '2022-07-05')
])
def test_clusters(config_default, test_source, test_symbol, time_begin, time_end):

    timeframe = '1h'

    indicators = lti.Indicators(test_source, time_begin, time_end)
    ohlcvm = indicators.OHLCVM(test_symbol, timeframe)

    ohlcvm.show()
