from preprocessing.data_ingest import data_in_csv
from preprocessing.timeframe import convert_timeframe
from Charts.candle_chart import interactive_candle_chart
from preprocessing.cleaning import data_cleaning
from preprocessing.indicator import sma, ema, rsi, macd, bollinger_bands, atr, garman_klass
from Evaluation.strategy_performance import strategy_performance
import pandas as pd
#from Practice.random import randomdate_data
#from Practice.plotter import plotter
#from Practice.performance import performance


data = data_in_csv('data/NIFTY50-Minute_data.csv')
data = data_cleaning(data)
data = convert_timeframe(data, '5min')

#indicators 

data = sma(data)
#data = ema(data)
#data = rsi(data)
#data = macd(data)
#data = bollinger_bands(data)
#data = atr(data)
#data = garman_klass(data
print(data.head(5))
print(data.tail(5))
print("Available strategies-'sma', 'bb', 'rsi', 'macd', 'idg', 'tfb', 'mr'")
strategy = input("Enter the strategy you want to implement: ")
close_capital ,pnl, points = strategy_performance(data, strategy , start_date="2020-01-01", end_date="2021-12-10", initial_capital=100000)
print(f"Close Capital: {close_capital}")
print(f"Points Captured: {points}")
print(f"Profit/Loss: {pnl}")

#fig = interactive_candle_chart(data, show_fig=True)
s