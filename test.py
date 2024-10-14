from Ingest.data_ingest import data_in_csv
from preprocessing.timeframe import convert_timeframe
from Charts.candle_chart import interactive_candle_chart
from Charts.mpl_candle import mpl_candlestick_chart
from preprocessing.cleaning import data_cleaning
from indicators.indicator import sma, ema, rsi, macd, bollinger_bands, atr, garman_klass
from Performance.stratergy_performance import stratergy_performance


data = data_in_csv('data/NIFTY50-Minute_data.csv')
data = data_cleaning(data)
data_5min = convert_timeframe(data, '5min')

data_5min = sma(data_5min)
data_5min = ema(data_5min)
data_5min = rsi(data_5min)
#data_5min = macd(data_5min)
#data_5min = bollinger_bands(data_5min)
#data_5min = atr(data_5min)
#data_5min = garman_klass(data_5min)
print(data_5min.head(100))

pnl, points = stratergy_performance(data_5min.head(1500), 'sma', start_date=None, end_date=None, initial_capital=100000)

print(f"Points Captured: {points}")
print(f"Profit/Loss: {pnl}")