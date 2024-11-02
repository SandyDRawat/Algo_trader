import pandas as pd
import numpy as np

def sma_strategy(data):
    """
    Implements a simple moving average crossover strategy.
    Adds a 'Buy/Sell' column where:
    - 1 indicates a buy signal (price crosses above the SMA)
    - -1 indicates a sell signal (price crosses below the SMA)

    Parameters:
    - data: DataFrame with 'Close' price and pre-calculated 'SMA'

    Returns:
    - DataFrame with an added 'Buy/Sell' column
    """
    # Check if 'SMA' column exists in the DataFrame
    if 'SMA' not in data.columns:
        raise ValueError("Data must contain an 'SMA' column")
    
    # Make a copy of the data to prevent SettingWithCopyWarning
    data = data.copy()

    # Initialize 'Buy/Sell' column with zeros
    data.loc[:, 'Buy/Sell'] = 0

    # Buy signal (1) when 'Close' crosses above 'SMA'
    data.loc[(data['Close'] > data['SMA']) & (data['Close'].shift(1) <= data['SMA'].shift(1)), 'Buy/Sell'] = 1

    # Sell signal (-1) when 'Close' crosses below 'SMA'
    data.loc[(data['Close'] < data['SMA']) & (data['Close'].shift(1) >= data['SMA'].shift(1)), 'Buy/Sell'] = -1

    return data
