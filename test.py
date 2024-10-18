from Ingest.data_ingest import data_in_csv
from preprocessing.timeframe import convert_timeframe
from Charts.candle_chart import interactive_candle_chart
from Charts.mpl_candle import mpl_candlestick_chart
from preprocessing.cleaning import data_cleaning
from indicators.indicator import sma, ema, rsi, macd, bollinger_bands, atr, garman_klass
from Performance.stratergy_performance import stratergy_performance
#from Practice.random import randomdate_data
#from Practice.plotter import plotter
#from Practice.performance import performance


data = data_in_csv('data/NIFTY50-Minute_data.csv')
data = data_cleaning(data)
#data_5min = convert_timeframe(data, '5min')
data_5min = convert_timeframe(data, '5min')

data = sma(data)
data = ema(data)
data = rsi(data)
#data = macd(data)
#data = bollinger_bands(data)
#data = atr(data)
#data = garman_klass(data)
print(data.head(200))


data_5min = sma(data_5min)
data_5min = ema(data_5min)
data_5min = rsi(data_5min)
print(data_5min.head(200))
#data_random = randomdate_data(data)
#data_after = plotter(data_random)
#print(performance(data_after))

pnl, points = stratergy_performance(data.head(5000), 'sma', start_date=None, end_date=None, initial_capital=100000)

print(f"Points Captured: {points}")
print(f"Profit/Loss: {pnl}")
#fig = interactive_candle_chart(data.head(1000), show_fig=True)
