import numpy as np
from packaging import version
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle
from matplotlib import ticker
from .constants import TIME_TYPE_UNIT, TIME_TYPE
from .exceptions import *
from .indicator_data import OHLCV_data

MATPLOTLIB_VERSION_REQUIRED = '3.5.1'

COLOR_UP = 'green'
COLOR_DOWN = 'red'
COLOR_MV = 'blue'
COLOR_HIST_UP = 'green'
COLOR_HIST_DOWN = 'red'

if version.parse(mpl.__version__) < version.parse(MATPLOTLIB_VERSION_REQUIRED):
    raise LTIException(f'Requires a version of matplotlib at least {MATPLOTLIB_VERSION_REQUIRED}')


@ticker.FuncFormatter
def volume_major_formatter(x, pos):

    if x == 0:
        return '0'
    elif x % 1000000000 == 0:
        return f'{int(x // 1000000000):d}G'
    elif x % 1000000 == 0:
        return f'{int(x // 1000000):d}M'
    elif x % 1000 == 0:
        return f'{int(x // 1000):d}K'
    elif x % 1 == 0:
        return f'{int(x):d}K'

    return f'{x}'


def indicator_data_plot(indicator_data):

    values_groups, ohlcv_data_matching = get_values_groups(indicator_data)

    plt.rcParams['axes.axisbelow'] = True

    n_indicator_axis = len(values_groups) - 1
    gridspec_kw = {'height_ratios': [3] + [1] + [1] * n_indicator_axis}
    fig, axis = plt.subplots(2 + n_indicator_axis, 1, sharex=True, dpi=200, gridspec_kw=gridspec_kw)
    fig.set_size_inches(8, 4.8)

    ax_price = axis[0]
    ax_volume = axis[1]
    plt.subplots_adjust(hspace=0)

    cdf = mpl.dates.ConciseDateFormatter(ax_price.xaxis.get_major_locator())
    ax_price.xaxis.set_major_formatter(cdf)

    timeframe = indicator_data.timeframe
    time = indicator_data.time
    symbol = indicator_data.symbol
    source = indicator_data.source

    if ohlcv_data_matching is None:

        if isinstance(indicator_data, OHLCV_data):
            ohlcv_data = indicator_data
        else:
            ohlcv_data = indicator_data.source_ohlcv()

        open = ohlcv_data.open
        high = ohlcv_data.high
        low = ohlcv_data.low
        close = ohlcv_data.close
        volume = ohlcv_data.volume

    else:

        open = indicator_data.data[ohlcv_data_matching['open']]
        high = indicator_data.data[ohlcv_data_matching['high']]
        low = indicator_data.data[ohlcv_data_matching['low']]
        close = indicator_data.data[ohlcv_data_matching['close']]
        volume = indicator_data.data[ohlcv_data_matching['volume']]

    plot_ohlcv(ax_price, timeframe, time, open, high, low, close)
    plot_volumes(ax_volume, timeframe, time, open, close, volume)

    for i_axis, values in enumerate(values_groups):

        if i_axis == 0:
            ax = axis[i_axis]
        else:
            ax = axis[i_axis + 1]

        for value_descript in values:

            value_parts = value_descript.split('=')
            value_name_descript = value_parts[0]

            value_parts_name = value_name_descript.split(':')
            value_name = value_parts_name[0]
            chart_type = value_parts_name[1] if len(value_parts_name) > 1 else None

            if len(value_parts) > 1:

                value = float(value_parts[1])
                if chart_type == 'ymin':
                    ax.set_ylim(bottom=value)
                    continue
                elif chart_type == 'ymax':
                    ax.set_ylim(top=value)
                    continue

                values = np.ones(len(time), dtype=float) * value

            else:
                values = indicator_data.data[value_name]

            plot_indicator(ax, timeframe, time, value_name, values, chart_type)

    need_legend = False
    for i_ax, ax in enumerate(axis):

        ax.grid(visible=True, linestyle=':')

        if i_ax == 0:
            ax_label = 'Price'
        elif i_ax == 1:
            ax_label = 'Volume'
            ax.yaxis.set_major_formatter(volume_major_formatter)
        elif i_ax > 1:
            ax_label = indicator_data.name
        else:
            ax_label = None

        if ax_label:
            ax.text(0.99, 0.97, ax_label, transform=ax.transAxes, verticalalignment='top', horizontalalignment='right')

        handles, labels = ax.get_legend_handles_labels()
        if len(handles) > 0:
            if need_legend or len(handles) >= (2 if i_ax > 0 and len(axis) < 4 else 1):
                ax.legend(loc='upper left', framealpha=0.5)
                need_legend = True

    parameters = indicator_data.data.get('parameters')
    if parameters is not None:
        ax_price.set_title(', '.join([f'{key}={value!r}' for key, value in parameters.items()]), fontsize='small')

    if isinstance(indicator_data, OHLCV_data):
        title = f'{symbol} {timeframe!s} [{source}]'
    else:
        title = f'{indicator_data.name} ({symbol} {timeframe!s} [{source}])'

    fig.suptitle(title)
    fig.canvas.manager.set_window_title(f'live_trading_indicators - {title}')
    return fig


def get_values_groups(indicator_data):

    if isinstance(indicator_data, OHLCV_data):
        charts = (None,)
    else:
        charts = indicator_data.data.get('charts')
        assert isinstance(charts, (tuple, type(None)))

    if charts is None:

        no_paint = {'time'}

        price_chart = set()
        for key, value in indicator_data.data.items():
            if type(value) == np.ndarray and key not in no_paint:
                price_chart.add(key)

        return [price_chart], None

    ohlcv_data_dict = None
    values_groups = []
    for values_list in charts:
        if values_list is None:
            values_set = set()
        elif isinstance(values_list, str):
            values_set = {value_name.strip() for value_name in values_list.split(',')}
        elif isinstance(values_list, tuple):
            values_set = set()
            for value in values_list:
                if isinstance(value, dict):
                    ohlcv_data_dict = value
                else:
                    values_set.add(value)

        values_groups.append(values_set)

    return values_groups, ohlcv_data_dict


def plot_indicator(axis, timeframe, time, name, values, chart_type=None):
    if chart_type is None:
        axis.plot(time, values, label=name)

    elif chart_type == 'bar_level':
        bar_marker_width = np.timedelta64(int(timeframe.value * 1.0), TIME_TYPE_UNIT)
        axis.bar(time, 0, bottom=values, width=bar_marker_width, linewidth=1, edgecolor=COLOR_MV, label=name)

    elif chart_type == 'hist':
        bar_width = np.timedelta64(timeframe.value // 3, TIME_TYPE_UNIT)
        axis.bar(time, values, width=bar_width, label=name)

    elif chart_type == 'histdiff':

        bar_width = np.timedelta64(int(timeframe.value * 0.6), TIME_TYPE_UNIT)

        diff = np.hstack([0.0, np.diff(values)])
        diff_0 = diff == 0
        diff_p = diff > 0
        diff_m = diff < 0

        axis.bar(time[diff_0], values[diff_0], width=bar_width, color='gray')
        axis.bar(time[diff_p], values[diff_p], width=bar_width, color=COLOR_HIST_UP)
        axis.bar(time[diff_m], values[diff_m], width=bar_width, color=COLOR_HIST_DOWN)

    elif chart_type == 'level':
        axis.plot(time, values, linestyle='dotted', color='black', linewidth=1)

    elif chart_type == 'pivots':
        bx_points = ~np.isnan(values)
        axis.plot(time[bx_points], values[bx_points], label=name)

    else:
        axis.plot(time, values, label=name, linestyle=chart_type)


def plot_ohlcv(axis, timeframe, time, open, high, low, close):

    ix_up_candles = close > open
    ix_down_candles = ~ix_up_candles

    ranges_body = abs(close - open)
    bottoms = np.vstack((close, open)).min(0)

    width_bar = np.timedelta64(int(timeframe.value * 0.8), TIME_TYPE_UNIT)
    width_tail = np.timedelta64(int(timeframe.value * 0.2), TIME_TYPE_UNIT)
    axis.bar(time[ix_up_candles], ranges_body[ix_up_candles], bottom=bottoms[ix_up_candles], color=COLOR_UP, width=width_bar)
    axis.bar(time[ix_down_candles], ranges_body[ix_down_candles], bottom=bottoms[ix_down_candles], color=COLOR_DOWN, width=width_bar)

    ranges_all = abs(high - low)
    axis.bar(time[ix_up_candles], ranges_all[ix_up_candles], bottom=low[ix_up_candles], color=COLOR_UP, width=width_tail)
    axis.bar(time[ix_down_candles], ranges_all[ix_down_candles], bottom=low[ix_down_candles], color=COLOR_DOWN, width=width_tail)


def plot_volumes(axis, timeframe, time, open, close, volume):

    width_bar = np.timedelta64(int(timeframe.value * 0.8), TIME_TYPE_UNIT)

    ix_up_candles = close > open
    ix_down_candles = ~ix_up_candles

    axis.bar(time[ix_up_candles], volume[ix_up_candles], color=COLOR_UP, width=width_bar)
    axis.bar(time[ix_down_candles], volume[ix_down_candles], color=COLOR_DOWN, width=width_bar)
