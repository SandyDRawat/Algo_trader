import pandas as pd
import numpy as np

def intraday_gap_strategy(data, target_gap_close=0.01):
    """
    Implements an intraday gap strategy that generates only buy/sell signals.
    - Buy when the stock opens much lower than the previous day's close (gap down).
    - Sell when the stock opens much higher than the previous day's close (gap up).
    - Close the position (sell) when the gap closes or reaches a specified target.

    Parameters:
    - data: DataFrame with 'Open' and 'Close' prices.
    - target_gap_close: The percentage change to consider the gap closed (default is 1%).

    Returns:
    - DataFrame with 'Buy/Sell' column, where 1 = Buy, -1 = Sell, and 0 = Hold.
    """
    # Initialize 'Buy/Sell' column with zeros (hold signal)
    data['Buy/Sell'] = 0

    # Calculate the gap from previous day's close to the current day's open
    data['Gap'] = data['Open'] - data['Close'].shift(1)

    # Buy signal for gap down (opens lower than previous close by a certain percentage)
    data.loc[data['Gap'] < -0.01 * data['Close'].shift(1), 'Buy/Sell'] = 1

    # Sell signal for gap up (opens higher than previous close by a certain percentage)
    data.loc[data['Gap'] > 0.01 * data['Close'].shift(1), 'Buy/Sell'] = -1


    position = 0
    # Check for gap close exit after a buy or sell signal
    for i in range(1, len(data)):
        # If the previous row was a buy signal and gap close hasn't been met, hold (0)
        if data['Buy/Sell'].iloc[i - 1]  == 1:
            entry_price = data['Open'].iloc[i - 1]
            gap_close_price = entry_price * (1 + target_gap_close)
            if data['Close'].iloc[i] >= gap_close_price:
                data.at[data.index[i], 'Buy/Sell'] = -1  # Close (sell) signal
            else:
                data.at[data.index[i], 'Buy/Sell'] = 0  # Hold signal

        # If the previous row was a sell signal and gap close hasn't been met, hold (0)
        elif data['Buy/Sell'].iloc[i - 1] == -1:
            entry_price = data['Open'].iloc[i - 1]
            gap_close_price = entry_price * (1 - target_gap_close)
            if data['Close'].iloc[i] <= gap_close_price:
                data.at[data.index[i], 'Buy/Sell'] = 1  # Close (buy) signal
            else:
                data.at[data.index[i], 'Buy/Sell'] = 0  # Hold signal

    # Remove temporary 'Gap' column
    data.drop(columns=['Gap'], inplace=True)

    return data
