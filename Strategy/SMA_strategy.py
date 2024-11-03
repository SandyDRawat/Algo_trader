import pandas as pd
import numpy as np

def sma_strategy(data):
    """
    Implements a simple moving average crossover strategy using a Position column.
    Adds a 'Position' column where:
    - 1 indicates holding a long position (price is above SMA).
    - -1 indicates holding a short position (price is below SMA).
    - 0 indicates no position (position closed).

    Parameters:
    - data: DataFrame with 'Close' price and pre-calculated 'SMA'.

    Returns:
    - DataFrame with an added 'Position' column.
    """
    # Check if 'SMA' column exists in the DataFrame
    if 'SMA' not in data.columns:
        raise ValueError("Data must contain an 'SMA' column")
    
    # Make a copy of the data to prevent SettingWithCopyWarning
    data = data.copy()

    # Initialize 'Position' column with zeros (no position)
    data['Position'] = 0

    # Define the conditions for entering and exiting positions
    for i in range(1, len(data)):
        # Check if previous position was flat (no position)
        if data['Position'].iloc[i - 1] == 0:
            # Enter a long position if Close crosses above SMA
            if data['Close'].iloc[i] > data['SMA'].iloc[i] and data['Close'].iloc[i - 1] <= data['SMA'].iloc[i - 1]:
                data.at[data.index[i], 'Position'] = 1  # Long position
            # Enter a short position if Close crosses below SMA
            elif data['Close'].iloc[i] < data['SMA'].iloc[i] and data['Close'].iloc[i - 1] >= data['SMA'].iloc[i - 1]:
                data.at[data.index[i], 'Position'] = -1  # Short position

        # If holding a long position, check if it should be closed or reversed
        elif data['Position'].iloc[i - 1] == 1:
            # Close long if Close crosses below SMA (exit)
            if data['Close'].iloc[i] < data['SMA'].iloc[i]:
                data.at[data.index[i], 'Position'] = 0  # Close long position
            else:
                data.at[data.index[i], 'Position'] = 1  # Maintain long position

        # If holding a short position, check if it should be closed or reversed
        elif data['Position'].iloc[i - 1] == -1:
            # Close short if Close crosses above SMA (exit)
            if data['Close'].iloc[i] > data['SMA'].iloc[i]:
                data.at[data.index[i], 'Position'] = 0  # Close short position
            else:
                data.at[data.index[i], 'Position'] = -1  # Maintain short position

    return data
