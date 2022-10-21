# fast_trading_indicators (в разработке)
Пакет для получения данных котировок из различных источников и расчета на основе этих котировок значений технических индикаторов.
# Источники данных
Текущая версия получает данные из одного источника - открытые данные торговли криптобиржи binance. Используются данные данные типа klines и trades. Имя источника "binance".
# Индикаторы
Реализованы следующие индикаторы:
EMA(?)
SMA(?)
MACD(?)
# Использование

## Введение

import fast_trading_indicators as fti

indicators = fti.Indicators('binance', 20210201, 20210202)

ohlcv = indicators.OHLCV('um/ethusdt', fti.Timeframe.t1h)
ohlcv
ohlcv.time
ohlcv.close
ohlcv.pandas()

ma22 = fti.indicators.SMA('um/ethusdt', fti.Timeframe.t1h, 'close', 22)
ma22
(ohlcv + ma22).pandas()

## Указание границ интервалов
Время во входных параметрах может иметь тип datetime или в виде целого числа YYYYMMDD:
indicators = fti.Indicators('binance', 20220901, 20220931)
fti.indicators.SMA('um/ethusdt', fti.Timeframe.t1h, 'close', 22, time_begin=dt.datetime(2022, 9, 1, 5, 40), time_end=dt.datetime(2022, 9, 1, 23, 59))

Существуют две стратегии указания периода времени.
### 1. Период времени указывается при создании Indicators
После этого все индикаторы будут расчитываться и сохранятся в кэше на укаанный интервал. Значения индикаторов можно получить за любой период в пределах интервала Indicators. При выходе за указанный интервал будет исключение FTIExceptionOutOfThePeriod.
#### Пример
indicators = fti.Indicators('binance', 20220901, 20220931)
ohlcv = indicators.OHLCV('um/ethusdt', fti.Timeframe.t1h)
ma22 = fti.indicators.SMA('um/ethusdt', fti.Timeframe.t1h, 'close', 22, time_begin=20220905, time_end=20220915)

### 2. Период времени указывается только при получении данных
В этом случае, при получении данных индикатора период надо использовать всегда. Период времени для расчета значений индикаторов определяется автоматически. При расширении интервала может происходит сброс кэша данных, это может замедлять работу.
#### Пример
indicators = fti.Indicators('binance')
ohlcv = indicators.OHLCV('um/ethusdt', fti.Timeframe.t1h, time_begin=20220801, time_end=20220815)
ma22 = fti.indicators.SMA('um/ethusdt', fti.Timeframe.t1h, 'close', 22, time_begin=20220905, time_end=20220915)
