# Benchmark results

- Symbol: ethusdt
- Timeframe: 1s
- Period: 2021-01-01T00:00 - 2021-12-31T23:59
- Number of quotes: 31 536 000
## Read quotes
```
<OHLCV data> symbol: ethusdt, timeframe: 1s
date: 2021-01-01T00:00 - 2021-12-31T23:59 (length: 31536000) 
Values: time, open, high, low, close, volume
4.66771782503929 seconds
```
## Indicators performance
```
<IndicatorData> name: SMA, symbol: ethusdt, timeframe: 1s, allowed nan
date: 2021-01-01T00:00 - 2021-12-31T23:59 (length: 31536000) 
Values: time, move_average
MA 0.5642972170026042 seconds

<IndicatorData> name: EMA, symbol: ethusdt, timeframe: 1s, allowed nan
date: 2021-01-01T00:00 - 2021-12-31T23:59 (length: 31536000) 
Values: time, ema
EMA 0.1669687769608572 seconds

<IndicatorData> name: Stochastic, symbol: ethusdt, timeframe: 1s, allowed nan
date: 2021-01-01T00:00 - 2021-12-31T23:59 (length: 31536000) 
Values: time, value_d, value_k, oscillator
Stochastic 1.9372139129554853 seconds
```
