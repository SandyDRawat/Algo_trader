import pandas as pd
import numpy as np

def mean_reversion_strategy(data, lookback=20):
    """
    Implements a mean reversion strategy.
    - Sets Position to 1 (long) when price falls significantly below the moving average (oversold condition).
    - Sets Position to -1 (short) when price rises significantly above the moving average (overbought condition).
    - Sets Position to 0 when there are no signals.

    Parameters:
    - data: DataFrame with 'Close' prices.
    - lookback: Lookback period for calculating the moving average.

    Returns:
    - DataFrame with added 'Moving Average', 'Deviation', and 'Position' columns.
    """
    # Calculate the moving average
    data['Moving Average'] = data['Close'].rolling(window=lookback).mean()

    # Calculate the deviation from the moving average
    data['Deviation'] = data['Close'] - data['Moving Average']

    # Calculate the standard deviation of the deviation over the lookback period
    deviation_std = data['Deviation'].rolling(window=lookback).std()

    # Initialize 'Position' column with zeros (no position)
    data['Position'] = 0

    # Set long position (1) when price is significantly below the moving average
    data.loc[data['Deviation'] < -2 * deviation_std, 'Position'] = 1

    # Set short position (-1) when price is significantly above the moving average
    data.loc[data['Deviation'] > 2 * deviation_std, 'Position'] = -1

    # Carry forward the position to the next rows until an opposite signal is generated
    data['Position'] = data['Position'].replace(to_replace=0, method='ffill').fillna(0)
    
    return data
