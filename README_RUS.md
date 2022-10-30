# live_trading_indicators
Пакет для получения данных котировок из различных источников онлайн и расчета на основе этих котировок значений технических индикаторов.
Запрос и загрузка данных происходит автоматически. Полученые данные сохраняются в кэше с возможностью быстрого использования. Производится тщательный контроль целостности данных.

Папка данных пакета по умолчанию .lti в домашней папке пользователя. В этой папке может создаваться значительный объем данных, в зависимости от количества инструментов и их таймфреймов.

## Примеры использования
### Получение котировок
```
import live_trading_indicators as lti

indicators = lti.Indicators('binance')
ohlcv = indicators.OHLCV('ethusdt', '4h', '2022-07-01', '2022-07-01')

time = ohlcv.time # numpy array
open = ohlcv.open # numpy array
high = ohlcv.high # numpy array
low = ohlcv.low # numpy array
close = ohlcv.close # numpy array
volume = ohlcv.volume # numpy array

```
### Получение котировок в pandas
dataframe = ohlcv.pandas() # pandas dataframe

Поддерживаются все типовые тамфреймы до 1 суток включительно: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d.
# Источники данных
Текущая версия получает данные из одного источника - открытые данные торговли криптобиржи binance. 
# Индикаторы
Реализованы следующие индикаторы:
- EMA(?)
- SMA(?)
- MACD(?)
# Использование

### Быстрый пример
```
import live_trading_indicators as lti

indicators = lti.Indicators('binance', 20210201, 20210202)

ohlcv = indicators.OHLCV('um/ethusdt', lti.Timeframe.t1h)
ohlcv
ohlcv.time
ohlcv.close
ohlcv.pandas()

ma22 = lti.indicators.SMA('um/ethusdt', lti.Timeframe.t1h, 'close', 22)
ma22
(ohlcv + ma22).pandas()
```
### Указание границ интервалов
Время во входных параметрах может иметь тип date, datetime, datetime64, строка ISO 8601, или в виде целого числа YYYYMMDD:
```
indicators = lti.Indicators('binance', 20220901, 20220931)
indicators.SMA('um/ethusdt', lti.Timeframe.t1h, 'close', 22, time_begin=dt.datetime(2022, 9, 1, 5, 40), time_end=dt.datetime(2022, 9, 1, 23, 59))
```

Существуют две стратегии указания периода времени.
#### 1. Период времени указывается при создании Indicators
После этого все индикаторы будут расчитываться и сохранятся в кэше на укаанный интервал. Значения индикаторов можно получить за любой период в пределах интервала Indicators. При выходе за указанный интервал будет исключение LTIExceptionOutOfThePeriod.
##### Пример
```
indicators = lti.Indicators('binance', 20220901, 20220931)
ohlcv = indicators.OHLCV('um/ethusdt', lti.Timeframe.t1h)
ma22 = indicators.SMA('um/ethusdt', lti.Timeframe.t1h, 'close', 22, time_begin=20220905, time_end=20220915)
```
#### 2. Период времени указывается только при получении данных
В этом варианте при получении данных индикатора период надо указывать всегда. Период времени для расчета значений индикаторов в кэше определяется автоматически. При расширении интервала может происходит сброс кэша, это может замедлять работу.
##### Пример
```
indicators = lti.Indicators('binance')
ohlcv = indicators.OHLCV('um/ethusdt', lti.Timeframe.t1h, time_begin=20220801, time_end=20220815)
ma22 = indicators.SMA('um/ethusdt', lti.Timeframe.t1h, 'close', 22, time_begin=20220905, time_end=20220915)
```
Примечание: При создании Indicators можно указать только одну из дат. В этом случае период расчета индикаторов так же будет изменятся, но одна граница интервала остается фиксированной.
