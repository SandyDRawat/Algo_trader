import pandas as pd
import numpy as np

def sma_stratergy(data):
    """
    Function to implement a simple moving average crossover strategy.
    Adds a 'Buy/Sell' column where:
    - 1 indicates a buy signal (price crosses above the SMA)
    - -1 indicates a sell signal (price crosses below the SMA)

    Parameters:
    - data: DataFrame with 'Close' price and pre-calculated 'SMA'

    Returns:
    - DataFrame with added 'Buy/Sell' column
    """
    # Ensure SMA exists in the data
    if 'SMA' not in data.columns:
        raise ValueError("Data must contain an 'SMA' column")

    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Generate buy signal (1) when price crosses above SMA
    data.loc[(data['Close'] > data['SMA']) & (data['Close'].shift(1) <= data['SMA'].shift(1)), 'Buy/Sell'] = 1

    # Generate sell signal (-1) when price crosses below SMA
    data.loc[(data['Close'] < data['SMA']) & (data['Close'].shift(1) >= data['SMA'].shift(1)), 'Buy/Sell'] = -1

    return data
