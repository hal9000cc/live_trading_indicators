import datetime as dt
import numpy as np
import os
import pickle


def compare_with_nan(value1, value2, accuracy=1e-08):

    ixb_nan1 = np.isnan(value1)
    ixb_nan2 = np.isnan(value2)

    if (ixb_nan1 != ixb_nan2).any():
        print(f'Not identical nan: {ixb_nan1.sum()}, {ixb_nan2.sum()}')
        return False

    if (~ixb_nan1).sum() == 0:
        return True

    max_error = abs(value1[~ixb_nan1] - value2[~ixb_nan1]).max()
    if max_error > accuracy:
        print(f'max error {max_error}')
        return False

    return True


def get_descript(args):

    if len(args) == 0:
        return ''

    return ','.join([str(par) for par in args])


def get_ref_values(name, ohlcv, series, *args):

    data_folder = os.path.join(os.getcwd(), 'data')

    symbol = ohlcv.symbol.replace('/', '_')
    time_begin = ohlcv.time[0].astype('datetime64[D]')
    time_end = ohlcv.time[-1].astype('datetime64[D]')
    par_decript = get_descript(args)
    ref_file_name = os.path.join(data_folder, f'{name}-{symbol}-{ohlcv.timeframe!s}-{time_begin}-{time_end}{par_decript}.test_dat')

    if os.path.isfile(ref_file_name):
        with open(ref_file_name, 'rb') as file:
            ref_values = pickle.load(file)
    else:

        from stock_indicators import Quote, EndType, ChandelierType, indicators as si

        def ohlcv2quote(ohlcv):
            time = ohlcv.time.astype(dt.datetime)
            return [Quote(time[i], ohlcv.open[i], ohlcv.high[i], ohlcv.low[i], ohlcv.close[i], ohlcv.volume[i]) for i in
                    range(len(ohlcv))]

        def stocks2numpy(stocks, variable):

            res = []
            for item in stocks:
                res.append(item.__getattribute__(variable))

            try:
                return np.array(res, dtype=float)
            except:
                return np.array(res)

        fun = getattr(si, name)
        if name == 'get_zig_zag':
            args = list(args)
            args[0] = EndType[args[0]]
            args = tuple(args)
        elif name == 'get_chandelier':
            args = list(args)
            args[2] = ChandelierType[args[2]]
            args = tuple(args)

        ind_data = fun(ohlcv2quote(ohlcv), *args)
        ref_values = {}
        for series_name in series.split(','):
            ref_values[series_name.strip()] = stocks2numpy(ind_data, series_name.strip())

    if time_end.tolist() < (dt.datetime.utcnow() - dt.timedelta(days=14)).date():
        with open(ref_file_name, 'wb') as file:
            pickle.dump(ref_values, file, 4)

    class Result:
        def __init__(self, data_dict):
            self.__dict__.update(data_dict)

    result = Result(ref_values)
    return result