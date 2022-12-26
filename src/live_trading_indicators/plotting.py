import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from .constants import TIME_TYPE_UNIT, TIME_TYPE

color_up = 'green'
color_down = 'red'


def indicator_data_plot(indicator_data):

    values_groups = get_values_groups(indicator_data)

    ohlcv_data = indicator_data.source_ohlcv()
    plt.rcParams['axes.axisbelow'] = True

    n_indicator_axis = len(values_groups) - 1
    gridspec_kw = {'height_ratios': [3] + [1] + [1] * n_indicator_axis}
    fig, axis = plt.subplots(2 + n_indicator_axis, 1, sharex=True, dpi=200, gridspec_kw=gridspec_kw)
    ax_price = axis[0]
    ax_volume = axis[1]
    plt.subplots_adjust(hspace=0, top=0.92)

    cdf = mpl.dates.ConciseDateFormatter(ax_price.xaxis.get_major_locator())
    ax_price.xaxis.set_major_formatter(cdf)

    plot_ohlcv(ohlcv_data, ax_price)

    time = indicator_data.time
    plot_volumes(ohlcv_data, ax_volume)

    for i_axis, values in enumerate(values_groups):

        if i_axis == 0:
            ax = axis[i_axis]
        else:
            ax = axis[i_axis + 1]
            #ax.set_ylabel(indicator_data.name)

        for value in values:
            plot_indicator(ax, value, time, indicator_data.data[value])

    for ax in axis:
        ax.grid(visible=True, linestyle=':')
        ax.legend()

    title = f'{indicator_data.name} ({ohlcv_data.symbol} {ohlcv_data.timeframe!s} [{ohlcv_data.source}])'
    ax_price.title.set_visible(False)
    fig.suptitle(title)
    fig.canvas.manager.set_window_title(title)
    return fig


def get_values_groups(indicator_data):

    charts = indicator_data.data.get('charts')

    if charts is None:

        no_paint = {'time'}

        price_chart = set()
        for key, value in indicator_data.data.items():
            if type(value) == np.ndarray and key not in no_paint:
                price_chart.add(key)

        return [price_chart]

    values_groups = []
    for values_list in charts:
        values_set = set() if values_list is None\
            else {value_name.strip() for value_name in values_list.split(',')}

        values_groups.append(values_set)

    return values_groups


def plot_indicator(ax, name, time, values):
    ax.plot(time, values, label=name)


def ohlcv_plot(ohlcv_data):

    plt.rcParams['axes.axisbelow'] = True

    fig, (ax_price, ax_volume) = plt.subplots(2, 1, sharex=True, dpi=200, gridspec_kw={'height_ratios': [3, 1]})
    plt.subplots_adjust(hspace=0, top=0.92)

    cdf = mpl.dates.ConciseDateFormatter(ax_price.xaxis.get_major_locator())
    ax_price.xaxis.set_major_formatter(cdf)

    ax_price.grid(visible=True, linestyle=':')
    ax_volume.grid(visible=True, linestyle=':')

    plot_ohlcv(ohlcv_data, ax_price)
    plot_volumes(ohlcv_data, ax_volume)

    title = f'{ohlcv_data.symbol} {ohlcv_data.timeframe!s} [{ohlcv_data.source}]'
    ax_price.title.set_visible(False)
    fig.suptitle(title)
    fig.canvas.manager.set_window_title(title)
    return fig


def plot_ohlcv(ohlcv_data, ax):

    #ax.set_ylabel('price')

    time = ohlcv_data.time
    ix_up_candles = ohlcv_data.close > ohlcv_data.open
    ix_down_candles = ~ix_up_candles

    ranges_body = abs(ohlcv_data.close - ohlcv_data.open)
    bottoms = np.vstack((ohlcv_data.close, ohlcv_data.open)).min(0)

    width_bar = np.timedelta64(int(ohlcv_data.timeframe.value * 0.8), TIME_TYPE_UNIT)
    width_tail = np.timedelta64(int(ohlcv_data.timeframe.value * 0.1), TIME_TYPE_UNIT)
    ax.bar(time[ix_up_candles], ranges_body[ix_up_candles], bottom=bottoms[ix_up_candles], color=color_up, width=width_bar)
    ax.bar(time[ix_down_candles], ranges_body[ix_down_candles], bottom=bottoms[ix_down_candles], color=color_down, width=width_bar)

    ranges_all = abs(ohlcv_data.high - ohlcv_data.low)
    ax.bar(time[ix_up_candles], ranges_all[ix_up_candles], bottom=ohlcv_data.low[ix_up_candles], color=color_up, width=width_tail)
    ax.bar(time[ix_down_candles], ranges_all[ix_down_candles], bottom=ohlcv_data.low[ix_down_candles], color=color_down, width=width_tail)


def plot_volumes(ohlcv_data, ax):

    #ax.set_ylabel('volume')

    time = ohlcv_data.time

    width_bar = np.timedelta64(int(ohlcv_data.timeframe.value * 0.8), TIME_TYPE_UNIT)

    ix_up_candles = ohlcv_data.close > ohlcv_data.open
    ix_down_candles = ~ix_up_candles

    ax.bar(time[ix_up_candles], ohlcv_data.volume[ix_up_candles], color=color_up, width=width_bar)
    ax.bar(time[ix_down_candles], ohlcv_data.volume[ix_down_candles], color=color_down, width=width_bar)
