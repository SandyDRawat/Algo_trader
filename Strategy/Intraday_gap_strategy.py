import pandas as pd
import numpy as np

def intraday_gap_strategy(data):
    """
    Implements an intraday gap strategy.
    - Buy when the stock opens much lower than the previous day's close (gap down).
    - Sell when the stock opens much higher than the previous day's close (gap up).

    Parameters:
    - data: DataFrame with 'Open' and 'Close' prices.

    Returns:
    - DataFrame with added 'Buy/Sell' column.
    """
    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Calculate the price gap from the previous day's close to the current day's open
    data['Gap'] = data['Open'] - data['Close'].shift(1)

    # Buy when the stock opens significantly lower than the previous close (gap down)
    data.loc[data['Gap'] < -0.01 * data['Close'].shift(1), 'Buy/Sell'] = 1

    # Sell when the stock opens significantly higher than the previous close (gap up)
    data.loc[data['Gap'] > 0.01 * data['Close'].shift(1), 'Buy/Sell'] = -1

    return data
