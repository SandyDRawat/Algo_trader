import pandas as pd
import numpy as np

def macd_strategy(data, short_window=12, long_window=26, signal_window=9):
    """
    Implements a MACD crossover strategy using a Position column.
    - Sets Position to 1 (long) when MACD crosses above the signal line.
    - Sets Position to -1 (short) when MACD crosses below the signal line.
    - Maintains Position based on the previous signal.

    Parameters:
    - data: DataFrame with 'Close' prices.
    - short_window: Short-term EMA period (default is 12).
    - long_window: Long-term EMA period (default is 26).
    - signal_window: Signal line EMA period (default is 9).

    Returns:
    - DataFrame with added 'MACD', 'Signal Line', and 'Position' columns.
    """
    # Calculate short-term and long-term EMAs
    data['EMA_short'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['EMA_long'] = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate MACD and Signal Line
    data['MACD'] = data['EMA_short'] - data['EMA_long']
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()

    # Initialize 'Position' column with zeros (no position)
    data['Position'] = 0

    # Set long position (1) when MACD crosses above the Signal Line
    data.loc[(data['MACD'] > data['Signal_Line']) & (data['MACD'].shift(1) <= data['Signal_Line'].shift(1)), 'Position'] = 1

    # Set short position (-1) when MACD crosses below the Signal Line
    data.loc[(data['MACD'] < data['Signal_Line']) & (data['MACD'].shift(1) >= data['Signal_Line'].shift(1)), 'Position'] = -1

    # Carry forward the position to the next rows until an opposite signal is generated
    data['Position'] = data['Position'].replace(to_replace=0, method='ffill').fillna(0)

    return data
