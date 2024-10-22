import pandas as pd
import numpy as np

def bollinger_band_strategy(data):
    """
    Function to implement a Bollinger Bands trading strategy.
    Adds a 'Buy/Sell' column where:
    - 1 indicates a buy signal (price crosses below the lower band)
    - -1 indicates a sell signal (price crosses above the upper band)

    Parameters:
    - data: DataFrame with 'Close' price, pre-calculated 'Upper Band' and 'Lower Band'

    Returns:
    - DataFrame with added 'Buy/Sell' column
    """
    # Ensure the necessary columns exist in the data
    if 'UpperBand' not in data.columns or 'LowerBand' not in data.columns:
        raise ValueError("Data must contain 'UpperBand' and 'LowerBand' columns")

    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Generate buy signal (1) when price crosses below the lower band
    data.loc[(data['Close'] < data['LowerBand']) & (data['Close'].shift(1) >= data['LowerBand'].shift(1)), 'Buy/Sell'] = 1

    # Generate sell signal (-1) when price crosses above the upper band
    data.loc[(data['Close'] > data['UpperBand']) & (data['Close'].shift(1) <= data['UpperBand'].shift(1)), 'Buy/Sell'] = -1

    return data
