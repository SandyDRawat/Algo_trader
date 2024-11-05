import pandas as pd
import numpy as np

def intraday_gap_strategy(data, target_gap_close=5, stop_loss=1):
    """
    Implements an intraday gap strategy with a 'Position' column for position tracking.
    - 1 indicates holding a long position (buy signal on gap down).
    - -1 indicates holding a short position (sell signal on gap up).
    - 0 indicates no position (position closed).

    Parameters:
    - data: DataFrame with 'Open' and 'Close' prices.
    - target_gap_close: The percentage change to consider the gap closed (default is 1%).

    Returns:
    - DataFrame with an added 'Position' column.
    """
    # Initialize 'Position' column with zeros (no position)
    data['Position'] = 0

    # Calculate the gap from the previous day's close to the current day's open
    data['Gap'] = data['Open'] - data['Close'].shift(1)
    print(data.columns)

    # Loop through each row in the DataFrame
    for i in range(1, len(data)):
        # If no position, check for entry signals
        if data['Position'].iloc[i - 1] == 0:
            # Buy signal for gap down (opens significantly lower than previous close)
            if (
            data['Gap'].iloc[i] < -0.01 * data['Close'].iloc[i - 1] 
            and data.index[i].hour == 9 
            and data.index[i].minute == 15
        ):
                data.at[data.index[i], 'Position'] = 1  # Long position
                target_price = data['Open'].iloc[i] * (1 + target_gap_close/100)
                stop_loss_price = data['Open'].iloc[i] * (1 - stop_loss / 100)

            # Sell signal for gap up (opens significantly higher than previous close)
            elif (
            data['Gap'].iloc[i] > 0.01 * data['Close'].iloc[i - 1] 
            and data.index[i].hour == 9 
            and data.index[i].minute == 15
        ):
                data.at[data.index[i], 'Position'] = -1  # Short position
                target_price = data['Open'].iloc[i] * (1 - target_gap_close/100)
                stop_loss_price = data['Open'].iloc[i] * (1 + stop_loss / 100)

        # If holding a long position, check if it should be closed
        elif data['Position'].iloc[i - 1] == 1:
            if data['Close'].iloc[i] >= target_price:
                data.at[data.index[i], 'Position'] = 0  # Close long position
            elif data['Close'].iloc[i] <= stop_loss_price:
                data.at[data.index[i], 'Position'] = 0
            elif data.index[i].hour == 15 and data.index[i].minute == 15:
                data.at[data.index[i], 'Position'] = 0
            else:
                data.at[data.index[i], 'Position'] = 1  # Maintain long position

        # If holding a short position, check if it should be closed
        elif data['Position'].iloc[i - 1] == -1:
            if data['Close'].iloc[i] <= target_price:
                data.at[data.index[i], 'Position'] = 0  # Close short position
            elif data['Close'].iloc[i] >= stop_loss_price:
                data.at[data.index[i], 'Position'] = 0
            elif data.index[i].hour == 15 and data.index[i].minute == 15:
                data.at[data.index[i], 'Position'] = 0
            else:
                data.at[data.index[i], 'Position'] = -1  # Maintain short position

    # Remove temporary 'Gap' column
    data.drop(columns=['Gap'], inplace=True)

    return data
