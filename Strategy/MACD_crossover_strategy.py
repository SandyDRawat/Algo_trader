import pandas as pd
import numpy as np

def macd_strategy(data, short_window=12, long_window=26, signal_window=9):
    """
    Implements a MACD crossover strategy.
    - Buy when MACD crosses above the signal line.
    - Sell when MACD crosses below the signal line.

    Parameters:
    - data: DataFrame with 'Close' prices.
    - short_window: Short-term EMA period (default is 12).
    - long_window: Long-term EMA period (default is 26).
    - signal_window: Signal line EMA period (default is 9).

    Returns:
    - DataFrame with added 'MACD', 'Signal Line', and 'Buy/Sell' columns.
    """
    # Calculate short-term and long-term EMA
    data['EMA_12'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate MACD and Signal line
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()

    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Buy when MACD crosses above the Signal line
    data.loc[(data['MACD'] > data['Signal Line']) & (data['MACD'].shift(1) <= data['Signal Line'].shift(1)), 'Buy/Sell'] = 1

    # Sell when MACD crosses below the Signal line
    data.loc[(data['MACD'] < data['Signal Line']) & (data['MACD'].shift(1) >= data['Signal Line'].shift(1)), 'Buy/Sell'] = -1

    return data
