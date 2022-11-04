# live_trading_indicators
A package for obtaining quotation data from various online sources and calculating the values of technical indicators based on these quotations.
Data is received automatically. It is possible to receive data in real time. The received data is stored in a file cache with the possibility of quick use. Data integrity is carefully monitored.

The current version allows you to receive exchange data **Binance** (**spot**, **futures USD-M**, **futures COIN-M**).

The data can be obtained in *numpy ndarray* and *Dataframe Pandas*..

Package data is stored by default in the *.lti* folder of of the user's home directory. A significant amount of data can be created in this folder, depending on the number of instruments and their timeframes.
## Installing
```python
pip install live_trading_indicators
```
## Usage examples
### Getting quotes
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

### pandas dataframe
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
### Example of getting indicator data
```python
macd = indicators.MACD('ethusdt', '1h', '2022-07-01', '2022-07-30', period_short=15, period_long=26, period_signal=9)
print(macd.pandas().head())
```
###### Result:
```
                 time      macd  macd_signal  macd_hist
0 2022-07-01 00:00:00  0.000000     0.000000   0.000000
1 2022-07-01 01:00:00  0.021389     0.010694   0.010694
2 2022-07-01 02:00:00 -0.061712    -0.013441  -0.048271
3 2022-07-01 03:00:00 -1.105457    -0.286445  -0.819012
4 2022-07-01 04:00:00 -2.146765    -0.658509  -1.488256
```
### Getting real-time data (the last 3 minutes on the 1m timeframe without an incomplete bar)
To get real-time data, you do not need to specify an end date.
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
2022-11-04 12:37:07,374 Download using api symbol btcusdt timeframe 1m from 2022-11-04T00:00:00.000...
                 time      open      high       low     close     volume
0 2022-11-04 09:34:00  20614.55  20618.50  20610.76  20615.97  263.96754
1 2022-11-04 09:35:00  20615.61  20624.00  20610.29  20616.53  258.53777
2 2022-11-04 09:36:00  20615.69  20617.75  20609.74  20611.46  199.43313
3 2022-11-04 09:37:00  20611.11  20611.89  20608.17  20609.02   15.15800
```
## Details
All typical tamframes are supported up to 1 day inclusive: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d.
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
When getting indicator values, the first two parameters should be symbol and timeframe. Further, the period can optionally be specified. Then the parameters of the indicator are specified by name.
#### Examples
```python
sma = indicators.MACD('ethusdt', '1h', period=9)
macd = indicators.MACD('ethusdt', '1h', '2022-07-01', '2022-07-30', period_short=15, period_long=26, period_signal=9)
```
The following indicators are implemented (the parameters *symbol*, *timeframe*, *time_start*, *time_end* are omitted for brevity):
- EMA(period, value='close')
- SMA(period, value='close')
- MA(period, value='close', ma_type='sma')
- MACD(period_short, period_long, period_signal)
- RSI(period, value='close')
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
indicators = lti.Indicators('binance') # период не указан
ohlcv = indicators.OHLCV('um/ethusdt', '1h', 20220801, 20220815) # период указывать обязательно
ma22 = indicators.SMA('um/ethusdt', '1h', 'close', 22, 20220905, 20220915) # период указывать обязательно
```
#### 3. Real-time mode
In this variant, when creating *Indicators*, only the start date is specified. The data is always received up to the current moment.
When creating Indicators, you can specify *with_incomplete_bar=True*, then the data of the last, incomplete bar will be received. See the example above.
### Binance trading symbol codes
- For the spot market, they completely coincide with the code on binance (*btcusdt*, *ethusdt*, etc.)
- For the futures market **USD-M**, codes are prefixed with **um/** (*um/btcusdt*, *um/ethusdt*, etc.)
- For the futures market **COIN-M**, codes are prefixed with **cm/** (*cm/btcusd_perp*, *cm/ethusd_perp*, etc.)
