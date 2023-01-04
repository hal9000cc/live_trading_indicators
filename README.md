# live_trading_indicators
[![PyPI version](https://badge.fury.io/py/live-trading-indicators.svg)](https://badge.fury.io/py/live-trading-indicators)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CodeQL](https://github.com/hal9000cc/live_trading_indicators/actions/workflows/codeql.yml/badge.svg)](https://github.com/hal9000cc/live_trading_indicators/actions/workflows/codeql.yml)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/live_trading_indicators.svg)](https://pypi.python.org/pypi/live_trading_indicators/)

A package for obtaining quotation data from various online and offline sources and calculating the values of technical indicators based on these quotations.
Data from online sources is received automatically. It is possible to receive data in real time. The received data is stored in a file cache with the possibility of quick use. Data integrity is carefully monitored.

In addition to receiving data online, Dataframe Pandas can be used as a data source.

The current version allows you to receive exchange data from:
- **Binance** (**spot**, **futures USD-M**, **futures COIN-M**).
- Many different exchanges via **CCXT** ([CryptoCurrency eXchange Trading Library](https://github.com/ccxt/ccxt#readme))

The data can be obtained in *numpy ndarray* and *Dataframe Pandas*..

Package data from online sources is stored by default in the *.lti* folder of the user's home directory. A significant amount of data can be created in this folder, depending on the number of instruments and their timeframes. Only data received from online sources is saved.
## Version 0.6.2
### what's new
#### 0.6.2
- New indicator - ZigZag
![live_trading_indicators - New indicator: ZigZag for BTCUSDT timeframe 4h](https://github.com/hal9000cc/live_trading_indicators/blob/stable/images/zigzag.png "live_trading_indicators - New indicator: ZigZag for BTCUSDT timeframe 4h")
#### 0.6.1
- Displaying indicator charts using matplotlib - [see](https://github.com/hal9000cc/live_trading_indicators/blob/stable/examples_show.ipynb).
- Repeated download attempts in case of errors (request_trys [setting](https://github.com/hal9000cc/live_trading_indicators/blob/stable/README.md#live_trading_indicators-library-settings)).
#### 0.5.3
- New timeframe - 1s
- Optimized loading of a large volume of quotes - [benchbarks](https://github.com/hal9000cc/live_trading_indicators/blob/stable/benchmarks.ipynb)
- Added intermediate saving when loading for a long time
#### 0.5.2
- Fix for python 3.7
#### 0.5.0
- Optimized data loading, reduced the number of requests to the data source on high timeframes.
- Added the ability to use the **CCXT** library as a data source.


[previous releases...](https://github.com/hal9000cc/live_trading_indicators/releases)
## Installing
```python
pip install live_trading_indicators
```
## Feedback
- [Discussions](https://github.com/hal9000cc/live_trading_indicators/discussions)
- [Issues](https://github.com/hal9000cc/live_trading_indicators/issues)
## Quick start
All the examples given here can be found in [jupyter notebook examples](https://github.com/hal9000cc/live_trading_indicators/blob/stable/examples.ipynb). There are also [benchmark results in jupyter notebook](https://github.com/hal9000cc/live_trading_indicators/blob/stable/benchmarks.ipynb).
### Getting quotes (online / cache)
```python
import live_trading_indicators as lti

indicators = lti.Indicators('binance')
ohlcv = indicators.OHLCV('ethusdt', '4h', '2022-07-01', '2022-07-01')
print(ohlcv)
```
###### Result:
```
<OHLCV data> symbol: ethusdt, timeframe: 4h
date: 2022-07-01T00:00 - 2022-07-01T20:00 (length: 6) 
empty bars: count 0 (0.00 %), max consecutive 0
Values: time, open, high, low, close, volume
```

Now *ohlcv* contains quotes in *numpy array* (*ohlcv.time*, *ohlcv.open*, *ohlcv.high*, *ohlcv.low*, *ohlcv.close*, *ohlcv.volume*).

### Export in pandas dataframe
```python
dataframe = ohlcv.pandas()
print(dataframe.head())
```
###### Result:
```
                 time     open     high      low    close       volume
0 2022-07-01 00:00:00  1071.02  1117.00  1050.46  1054.52  430646.8720
1 2022-07-01 04:00:00  1054.52  1076.43  1045.41  1066.81  275557.9328
2 2022-07-01 08:00:00  1066.81  1086.44  1033.44  1050.22  252105.5665
3 2022-07-01 12:00:00  1050.21  1074.23  1043.00  1056.86  298465.0695
4 2022-07-01 16:00:00  1056.86  1083.10  1054.82  1067.91  158796.2248
```
### Example of getting indicator data from Bybit quotes via ccxt (online / cache)
```python
import live_trading_indicators as lti

indicators = lti.Indicators('ccxt.bybit')
macd = indicators.MACD('ETHUSDT', '1h', '2022-07-01', '2022-07-30', period_short=15, period_long=26, period_signal=9)
print(macd[40:].pandas().head())
```
###### Result:
```
                 time      macd    signal      hist
0 2022-07-02 16:00:00 -1.661969 -3.514499  1.852530
1 2022-07-02 17:00:00 -0.983912 -3.125461  2.141548
2 2022-07-02 18:00:00 -0.081701 -2.617233  2.535532
3 2022-07-02 19:00:00  0.464134 -2.064394  2.528529
4 2022-07-02 20:00:00  0.828222 -1.477419  2.305641
```
### Example of getting indicator data from Pandas quotes
```python
import pandas
import live_trading_indicators as lti

dataframe = pandas.read_csv('tests/data/ETHUSDT-1m-2022-08-15.zip', header=None)
dataframe.rename(columns={0: 'time', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume', }, inplace=True)
indicators = lti.Indicators(dataframe)
macd = indicators.MACD(period_short=15, period_long=26, period_signal=9)
print(macd[40:].pandas().head())
```
###### Result:
```
                 time      macd    signal      hist
0 2022-08-15 00:40:00  3.403958  2.320975  1.082984
1 2022-08-15 00:41:00  3.540428  2.643593  0.896835
2 2022-08-15 00:42:00  3.594786  2.930063  0.664722
3 2022-08-15 00:43:00  3.684476  3.170449  0.514027
4 2022-08-15 00:44:00  3.763257  3.354183  0.409074
```
### Getting real-time data (the last 3 minutes on the 1m timeframe without an incomplete bar)
To get real-time data, you **don't have to specify an end date**.
```python
import datetime as dt
import live_trading_indicators as lti

utcnow = dt.datetime.utcnow()
print(f'Now is {utcnow} UTC')
indicators = lti.Indicators('binance', utcnow - dt.timedelta(minutes=3))
ohlcv = indicators.OHLCV('btcusdt', '1m')
print(ohlcv.pandas())
```
###### Result:
```
Now is 2022-11-04 09:32:31.528230 UTC
                 time      open      high       low     close     volume
0 2022-11-04 09:29:00  20594.39  20595.60  20591.06  20592.38  177.35380
1 2022-11-04 09:30:00  20592.38  20600.98  20591.75  20600.30  178.40869
2 2022-11-04 09:31:00  20600.98  20623.93  20600.30  20621.45  431.11917
```
### Getting real-time data (the last 3 minutes on the 1m timeframe and an incomplete bar)
To get data containing an incomplete bar, you must specify *with_incomplete_bar=True* when creating *Indicators*.
```python
utcnow = dt.datetime.utcnow()
print(f'Now is {utcnow} UTC')
indicators = lti.Indicators('binance', utcnow - dt.timedelta(minutes=3), with_incomplete_bar=True)
ohlcv = indicators.OHLCV('btcusdt', '1m')
print(ohlcv.pandas())
```
###### Result:
```
Now is 2022-11-04 09:37:07.372986 UTC
                 time      open      high       low     close     volume
0 2022-11-04 09:34:00  20614.55  20618.50  20610.76  20615.97  263.96754
1 2022-11-04 09:35:00  20615.61  20624.00  20610.29  20616.53  258.53777
2 2022-11-04 09:36:00  20615.69  20617.75  20609.74  20611.46  199.43313
3 2022-11-04 09:37:00  20611.11  20611.89  20608.17  20609.02   15.15800
```
### Plotting indicators charts
Plotting uses matplotlib. These are optional features, so matplotlib must be installed separately.
There are two methods for plotting: plot() and show(). plot() returns the drawn figure, show() returns None. For jupyter notepad, it is better to use show(), since plot() can draw a figure twice.
```python
indicators = lti.Indicators('binance', '2022-07-01', '2022-07-15')
bb = indicators.BollingerBands('btcusdt', '4h', '2022-07-05', '2022-07-15', period=14)
bb.show()
```
###### Result:
![live_trading_indicators library example chart: Bollinger bands for BTCUSDT timeframe 4h](https://github.com/hal9000cc/live_trading_indicators/blob/stable/images/bb_show_example.png "live_trading_indicators library example chart: Bollinger bands for BTCUSDT timeframe 4h")
## Details
live-trading-indicators supports the following timeframes: 1s, 1m, 3m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d.
The specific supported timeframes for the source depend on the source.
### Сhecking quotes
**live-trading-indicators** check the integrity of quotes when they are loaded.
The fraction of lost quotes should not exceed max_empty_bars_fraction. The number of lost quotes in a row should not exceed max_empty_bars_consecutive.
The values of max_empty_bars_fraction and max_empty_bars_consecutive are set to 0 by default. That is, if there is at least one lost quote, LTIExceptionTooManyEmptyBars will be raised:
```
live_trading_indicators.exceptions.LTIExceptionTooManyEmptyBars: Too many empty bars: fraction 0.014076769406392695, consecutive 79200. Source binance, symbol ethusdt, timeframe 1s, date 2021-01-01T00:00:00.000 - 2021-12-31T23:59:59.000.
```
The values of max_empty_bars_fraction and max_empty_bars_consecutive can be set as follows:
```
import live_trading_indicators as lti
lti.config(max_empty_bars_fraction=0.1, max_empty_bars_consecutive=10)
```
If you don't need integrity control at all, do:
```
import live_trading_indicators as lti
lti.config(max_empty_bars_fraction=-1, max_empty_bars_consecutive=-1)
```
The presence of the first and last bars in the date range is also checked. For more details, see [Settings](https://github.com/hal9000cc/live_trading_indicators/blob/stable/README.md#live_trading_indicators-library-settings).
### Informational messages
By default, log messages are output to the console, and you will see similar messages:
```
2022-11-04 12:32:31,528 Download using api symbol btcusdt timeframe 1m from 2022-11-04T00:00:00.000...
```
To disable these messages, run the following code and restart python.
```python
import live_trading_indicators as lti
lti.config(print_log=False)
```
### Indicators
When getting indicator values from **online** source, the first two parameters should be *symbol* and *timeframe*. Further, the period can optionally be specified. Then the parameters of the indicator are specified by name.
When getting indicator values **offline** from Pandas DataFrame parameters *symbol* and *timeframe* are **not specified**. 
#### Example (online)
```python
indicators = lti.Indicators('binance', '2022-07-01', '2022-08-30')
sma = indicators.SMA('ethusdt', '1h', period=9)
macd = indicators.MACD('ethusdt', '1h', '2022-07-01', '2022-07-30', period_short=15, period_long=26, period_signal=9)
```
#### Example (offline)
```python
dataframe = pandas.readcsv('ETHUSDT-1m-2022-08-15.zip')
indicators = lti.Indicators(dataframe)
macd = indicators.MACD(period_short=15, period_long=26, period_signal=9)
sma = indicators.SMA('2022-08-15T03:00', '2022-08-15T06:00', period=9)
```
The list of supported indicators and their parameters can be obtained by calling lti.help(). Parameters *symbol*, *timeframe*, *time_start*, *time_end* are omitted for brevity.
```python
import live_trading_indicators as lti
print(lti.help())
```
- ADX(period=14, smooth=14, ma_type='mma') - Average directional movement index.
- ATR(smooth=14, ma_type='mma') - Average true range.
- Awesome(period_fast=5, period_slow=34, ma_type_fast='smw', ma_type_slow='sma', normalized=False) - Awesome oscillator.
- BollingerBands(period=20, deviation=2, ma_type='sma', value='close') - Bollinger bands.
- CCI(period=) - Commodity channel index.
- EMA(period=, value='close') - Exponential moving average.
- Keltner(period=10, multiplier=1, period_atr=10, ma_type='ema', ma_type_atr='mma') - Keltner channel.
- MA(period=, value='close', ma_type='sma') - Moving average of different types: 'sma', 'ema', 'mma', 'ema0', 'mma0'
- MACD(period_short=, period_long=, period_signal=, ma_type='ema', ma_type_signal='sma', value='close') - Moving Average Convergence/Divergence.
- OBV() - On Balance Volume.
- OHLCV() - Quotes: open, high, low, close, volume.
- OHLCVM(timeframe_low='1m', bars_on_bins=6) - Quotes and the price of the maximum volume: open, high, low, close, volume, mv_price.
- ParabolicSAR(start=0.02, maximum=0.2, increment=0.02) - Parabolic SAR.
- ROC(period=14, ma_period=14, ma_type='sma', value='close') - Rate of Change.
- RSI(period=, ma_type='mma', value='close') - Relative strength index.
- SMA(period=, value='close') - Simple moving average.
- Stochastic(period=, period_d=, smooth=3, ma_type='sma') - Stochastic oscillator.
- Supertrend(period=10, multipler=3, ma_type='mma') - Supertrend indicator.
- TEMA(period=, value='close') - Triple exponential moving average.
- TRIX(period=, value='close') - TRIX oscillator.
- VWAP() - Volume-weighted average price.
- VWMA(period=, value='close') - Volume Weighted Moving Average.
- VolumeClusters(timeframe_low='1m', bars_on_bins=6) - OHLCVM and volume clusters is determined by the lower timeframe.
- ZigZag_pivots(delta=0.02, type='high_low', redrawable=False) - Zig-zag indicator (pivots).
### Specifying the period
The period can be specified both during initialization of *Indicators* and in the indicator parameters. The data type when specifying the period can be *datetime.date*, *datetime.datetime*, *numpy.datetime64*, string, or a number in the format *YYYYMMDD*.

There are three strategies for specifying a time period:
#### 1. The time period is specified when creating Indicators (base period)
Indicator values can be obtained for any period within the interval specified for *Indicators*. When exiting the specified interval, an exception will be raised *LTIExceptionOutOfThePeriod*.
##### Example
```python
indicators = lti.Indicators('binance', 20220901, 20220930) # the base period
ohlcv = indicators.OHLCV('um/ethusdt', '1h') # the period is not specified, the base period is used
sma22 = indicators.SMA('um/ethusdt', '1h', 20220905, 20220915, period=22) # the period is specified
sma15 = indicators.SMA('um/ethusdt', '1h', 20220905, 20221015, period=15) # ERROR, going beyond the boundaries of the base period
```
#### 2. The time period is not specified when creating Indicators
In this variant, when getting indicator data, the period should always be specified. When the interval is extended, data may be updated, this may slow down the work.
##### Example
```python
indicators = lti.Indicators('binance') # period not specified
ohlcv = indicators.OHLCV('um/ethusdt', '1h', 20220801, 20220815) # the period must be specified
ma22 = indicators.SMA('um/ethusdt', '1h', 'close', 22, 20220905, 20220915) # the period must be specified
```
#### 3. Real-time mode
In this variant, when creating *Indicators*, only the start date is specified. The data is always received up to the current moment.
When creating Indicators, you can specify *with_incomplete_bar=True*, then the data of the last, incomplete bar will be received. See the example above.
### Binance source
#### Binance trading symbol codes
- For the spot market, they completely coincide with the code on binance (*btcusdt*, *ethusdt*, etc.)
- For the futures market **USD-M**, codes are prefixed with **um/** (*um/btcusdt*, *um/ethusdt*, etc.)
- For the futures market **COIN-M**, codes are prefixed with **cm/** (*cm/btcusd_perp*, *cm/ethusd_perp*, etc.)
### CCXT source
Using CCXT, you can download data from a large number of exchanges, currently there are more than 100. The available symbols, their names and timeframes depend on the specific source. More information can be found in [the CCXT documentation.](https://github.com/ccxt/ccxt#readme)
The use of ccxt is optional, so it must be installed separately. It can be done like this:
```
pip install ccxt
```
Then you can use all available ccxt exchanges by specifying them through a dot. To download, for example, from binance via ccxt, you need to specify ccxt.binance. To download from okx, we use ccxt.okx, Bybit - ccxt.bybit, etc.
##### Example
```python
indicators = lti.Indicators('ccxt.okx')
ohlcv = indicators.OHLCV('BTC/USDT', '1h', 20220701, 20220702)
```
**live-trading-indicators** has not been tested with all quotation sources supported by **ccxt**. If you find a problem with some data source, open the problem [here](https://github.com/hal9000cc/live_trading_indicators/issues).

Sometimes the **ccxt** source may need additional parameters passed through *params*. In this case, these parameters are passed via *exchange_params* when creating *Indicators*:
```python
indicators = lti.Indicators('ccxt.okx', exchange_params={'limit': 300})
```
### Types of move average
live-trading-indicators supports the following types of moving averages:
- 'sma' - simple move average
- 'ema' - classical exponential moving average with alpha = 2 / (n + 1), initialized by SMA (as in binance EMA)
- 'ema0' - classical exponential moving average with alpha = 2 / (n + 1), initialized by the first value
- 'mma' - Modified moving average with alpha = 1 / n, initialized by SMA (as in some binance indicators)
- 'mma0' - Modified moving average с alpha = 1 / n, initialized by the first value

## live_trading_indicators library settings
The settings can be obtained as dict using *config()*:
```python
import live_trading_indicators as lti
print(lti.config())
```
Result:
```
{'cache_folder': '/home/user/.lti/data/timeframe_data', 'sources_folder': '/home/user/.lti/data/sources', 'log_folder': '/home/hal/.lti/logs', 'endpoints_required': True, 'max_empty_bars_fraction': 0.0, 'max_empty_bars_consecutive': 0, 'restore_empty_bars': True, 'print_log': True, 'log_level': 'INFO', 'request_timeout': 10, 'request_trys': 3}
```
*config()* is also used to change the settings:
```python
import live_trading_indicators as lti
lti.config(request_timeout=15)
```
When creating Indicators, you can specify the settings that will be used instead of the saved ones:
```python
    indicators = lti.Indicators(test_source, time_begin, time_end, timeout=15, request_trys=5)
```
### Settings
#### cache_folder
Directory for storing quotation data.
#### log_folder
Directory of log files.
#### endpoints_required
Control of the presence of the first and last bar in the selected date range. In the absence of the first or last bar, LTIExceptionQuotationDataNotFound is raised. Default: True.
#### max_empty_bars_fraction
The maximum percentage of lost bars, if exceeded, an error will occur.
#### max_empty_bars_consecutive
The maximum number of lost bars in a row, if exceeded, LTIExceptionTooManyEmptyBars will be raised.
#### restore_empty_bars
If True, it restores the lost bars (open=close=close of the previous one, volume=0). The control of the number of lost bars (max_empty_bars_fraction, max_empty_bars_consecutive) is performed BEFORE recovery. Default: True.
#### print_log
If True, outputs log messages to standard output. Default: True.
#### log_level
Log registration level. Default: INFO.
#### request_timeout
Timeout of requests to download quotes, seconds. Default: 10.
#### request_trys
The number of attempts to download quotes. Default: 3.
