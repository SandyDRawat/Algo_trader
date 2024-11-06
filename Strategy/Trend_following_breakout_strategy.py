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
    - DataFrame with added 'HHigh', 'LLow', and 'Position' columns.
    """
    # Calculate the highest high and lowest low over the lookback period
    data['HHigh'] = data['Close'].rolling(window=lookback, min_periods=1).max()
    data['LLow'] = data['Close'].rolling(window=lookback, min_periods=1).min()

    # Initialize 'Position' column with zeros (no position)
    data['Position'] = 0

    # Generate buy and sell signals
    data.loc[data['Close'] > data['HHigh'].shift(1), 'Position'] = 1   # Buy signal
    data.loc[data['Close'] < data['LLow'].shift(1), 'Position'] = -1   # Sell signal

    # Forward fill the positions to maintain trades until an opposite signal occurs
    data['Position'] = data['Position'].replace(0, np.nan).ffill().fillna(0)


    return data
