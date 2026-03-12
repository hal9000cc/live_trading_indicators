import numpy as np
import pytest
import ccxt
import live_trading_indicators as lti
from live_trading_indicators.timeframe import Timeframe


def fetch_monthly_ohlcv_direct(ccxt_source, symbol, time_begin, time_end):
    exchange = getattr(ccxt, ccxt_source)()
    since = int(np.datetime64(time_begin).astype('datetime64[ms]').astype(np.int64))
    limit = 12

    raw = exchange.fetch_ohlcv(symbol, '1M', since=since, limit=limit)

    time_end_month = np.datetime64(time_end).astype('datetime64[M]')
    filtered = [
        row for row in raw
        if np.datetime64(int(row[0]), 'ms').astype('datetime64[M]') <= time_end_month
    ]

    return (
        np.array([item[0] for item in filtered], dtype='datetime64[ms]'),
        np.array([item[1] for item in filtered], dtype=float),
        np.array([item[2] for item in filtered], dtype=float),
        np.array([item[3] for item in filtered], dtype=float),
        np.array([item[4] for item in filtered], dtype=float),
        np.array([item[5] for item in filtered], dtype=float),
    )


@pytest.mark.parametrize('ccxt_source, symbol', [
    ('binance', 'BTC/USDT'),
    ('bybit', 'BTC/USDT'),
])
def test_calendar_1m_matches_ccxt_exchange(clear_data, ccxt_source, symbol):

    time_begin = '2024-01-01'
    time_end = '2024-06-30'

    indicators = lti.Indicators(
        f'ccxt.{ccxt_source}',
        time_begin,
        time_end,
        max_empty_bars_consecutive=5,
        max_empty_bars_fraction=0.5,
        **clear_data,
    )
    ohlcv_lti = indicators.OHLCV(symbol, '1M')

    time_ccxt, open_ccxt, high_ccxt, low_ccxt, close_ccxt, volume_ccxt = fetch_monthly_ohlcv_direct(
        ccxt_source,
        symbol,
        time_begin,
        time_end,
    )

    assert len(ohlcv_lti.time) > 0
    assert len(ohlcv_lti.time) == len(time_ccxt)
    assert np.array_equal(ohlcv_lti.time.astype('datetime64[ms]'), time_ccxt)
    assert np.array_equal(ohlcv_lti.open, open_ccxt)
    assert np.array_equal(ohlcv_lti.high, high_ccxt)
    assert np.array_equal(ohlcv_lti.low, low_ccxt)
    assert np.array_equal(ohlcv_lti.close, close_ccxt)
    assert np.allclose(ohlcv_lti.volume, volume_ccxt)


def test_calendar_volume_indicators_match_manual_4h(clear_data):

    time_begin = '2024-01-01'
    time_end = '2024-06-30'
    symbol = 'BTC/USDT'

    indicators = lti.Indicators(
        'ccxt.binance',
        time_begin,
        time_end,
        max_empty_bars_consecutive=5,
        max_empty_bars_fraction=0.5,
        **clear_data,
    )

    ohlcvm = indicators.OHLCVM(symbol, '1M', timeframe_low='4h')
    clusters = indicators.VolumeClusters(symbol, '1M', timeframe_low='4h')
    bars_4h = indicators.OHLCV(symbol, '4h')

    assert len(ohlcvm) > 0
    assert len(ohlcvm) == len(clusters)
    assert (ohlcvm.time == clusters.time).all()
    assert (ohlcvm.open == clusters.open).all()
    assert (ohlcvm.high == clusters.high).all()
    assert (ohlcvm.low == clusters.low).all()
    assert (ohlcvm.close == clusters.close).all()
    assert np.allclose(ohlcvm.volume, clusters.volume)
    assert np.allclose(ohlcvm.mv_price, clusters.mv_price)

    min_low_bars = min(
        (ohlcvm.timeframe.next_bar_time(time) - time).astype(np.int64) // Timeframe.t4h.value
        for time in ohlcvm.time
    )
    expected_bins = int(min_low_bars // 5)

    assert clusters.clusters_volume.shape == (len(clusters), expected_bins)
    assert clusters.clusters_price.shape == (len(clusters), expected_bins + 1)

    for i_bar, time in enumerate(ohlcvm.time):
        time_next = ohlcvm.timeframe.next_bar_time(time)
        i_begin = int(np.searchsorted(bars_4h.time, time, side='left'))
        i_end = int(np.searchsorted(bars_4h.time, time_next, side='left'))
        bars_slice = bars_4h[i_begin:i_end]

        assert len(bars_slice) > 0
        assert bars_slice.time[0] == time
        assert bars_slice.time[-1] + Timeframe.t4h.value == time_next

        assert bars_slice.open[0] == ohlcvm.open[i_bar]
        assert bars_slice.close[-1] == ohlcvm.close[i_bar]
        assert bars_slice.high.max() == ohlcvm.high[i_bar]
        assert bars_slice.low.min() == ohlcvm.low[i_bar]
        assert np.isclose(bars_slice.volume.sum(), ohlcvm.volume[i_bar])

        hist, prices = np.histogram(
            np.hstack((bars_slice.high, bars_slice.low, bars_slice.close)),
            bins=expected_bins,
            weights=np.hstack((bars_slice.volume / 3, bars_slice.volume / 3, bars_slice.volume / 3))
        )

        assert np.allclose(hist, clusters.clusters_volume[i_bar])
        assert np.allclose(prices, clusters.clusters_price[i_bar])

        i_mv = hist.argmax()
        mv_price = (prices[i_mv] + prices[i_mv + 1]) / 2
        assert np.isclose(mv_price, ohlcvm.mv_price[i_bar])