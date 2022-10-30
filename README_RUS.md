# live_trading_indicators
Пакет для получения данных котировок из различных источников онлайн и расчета на основе этих котировок значений технических индикаторов.
Запрос и загрузка данных происходит автоматически. Полученые данные сохраняются в кэше с возможностью быстрого использования. Производится тщательный контроль целостности данных. Возможно получение данных в реальном времени.

Папка данных пакета по умолчанию .lti в домашней папке пользователя. В этой папке может создаваться значительный объем данных, в зависимости от количества инструментов и их таймфреймов.

## Примеры использования
### Получение котировок
```
import live_trading_indicators as lti

indicators = lti.Indicators('binance')
ohlcv = indicators.OHLCV('ethusdt', '4h', '2022-07-01', '2022-07-01')
print(ohlcv)
```
Теперь ohlcv содержит котировки в виде numpy array (ohlcv.time, ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume).

### pandas dataframe
```
dataframe = ohlcv.pandas()
dataframe.head()
```
### MACD индикатор
```
macd = indicators.MACD('ethusdt', '1h', '2022-07-01', '2022-07-30', period_short=15, period_long=26, period_signal=9)
macd.pandas().head()
```
### Получение данных в реальном времени (последние 5 минут на таймфрейме 1m без неполного бара)
```
import datetime as dt
import live_trading_indicators as lti

indicators = lti.Indicators('binance'. dt.datetime.utcnow() - dt.timedelta(minutes=6))
indicators.OHLCV('btcusdt', '1m').pandas().head()
```
### Получение данных в реальном времени (последние 5 минут на таймфрейме 1m с неполным баром)
```
import datetime as dt
import live_trading_indicators as lti

indicators = lti.Indicators('binance'. dt.datetime.utcnow() - dt.timedelta(minutes=5))
indicators.OHLCV('btcusdt', '1m').pandas().head()
```
## Подробнее
Поддерживаются все типовые тамфреймы до 1 суток включительно: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d.
### Источники данных
Текущая версия получает данные из одного источника - открытые данные торговли криптобиржи binance. 
### Индикаторы
Реализованы следующие индикаторы:
- EMA(period, value='close')
- SMA(period, value='close')
- MACD(period_short, period_long, period_signal)
- RSI(period, value)
### Использование
Существуют три стратегии указания периода времени.
#### 1. Период времени указывается при создании Indicators
После этого все индикаторы будут расчитываться и сохранятся в кэше на укаанный интервал. Значения индикаторов можно получить за любой период в пределах интервала Indicators. При выходе за указанный интервал будет сгенерировано исключение ?.
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
#### 3. Режим реального времени
В этом варианте при создании Indicators указывается только начальная дата интервала. Данные будут получены по текущий момент времени.
#### Пример
