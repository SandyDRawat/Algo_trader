import pandas as pd
import numpy as np

def breakout_strategy(data, lookback=20):
    """
    Implements a breakout strategy.
    - Buy when price breaks above the highest high over the lookback period.
    - Sell when price breaks below the lowest low over the lookback period.

    Parameters:
    - data: DataFrame with 'Close' prices.
    - lookback: Lookback period for identifying breakout levels (default is 20).

    Returns:
    - DataFrame with added 'High', 'Low', and 'Buy/Sell' columns.
    """
    # Calculate the highest high and lowest low over the lookback period
    data['High'] = data['Close'].rolling(window=lookback).max()
    data['Low'] = data['Close'].rolling(window=lookback).min()

    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Buy when the price breaks above the highest high
    data.loc[(data['Close'] > data['High']) & (data['Close'].shift(1) <= data['High'].shift(1)), 'Buy/Sell'] = 1

    # Sell when the price breaks below the lowest low
    data.loc[(data['Close'] < data['Low']) & (data['Close'].shift(1) >= data['Low'].shift(1)), 'Buy/Sell'] = -1

    return data
