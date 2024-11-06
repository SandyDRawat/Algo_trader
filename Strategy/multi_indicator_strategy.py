import pandas as pd
import numpy as np

def multi_indicator_strategy(data, fast_window=10, slow_window=50, rsi_period=14, overbought=70, oversold=30):
    """
    Multi-Indicator Strategy combining Moving Average Crossover and RSI for trend-following and mean-reversion.
    
    - Buy when the fast MA crosses above the slow MA and RSI is not overbought.
    - Sell when the fast MA crosses below the slow MA and RSI is not oversold.
    
    Parameters:
    - data: DataFrame with 'Close' prices.
    - fast_window: Fast-moving average period (default is 10).
    - slow_window: Slow-moving average period (default is 50).
    - rsi_period: RSI calculation period (default is 14).
    - overbought: RSI level to avoid entering new long positions (default is 70).
    - oversold: RSI level to avoid entering new short positions (default is 30).
    
    Returns:
    - DataFrame with added 'Fast_MA', 'Slow_MA', 'RSI', and 'Position' columns.
    """
    # Calculate moving averages
    data['Fast_MA'] = data['Close'].rolling(window=fast_window).mean()
    data['Slow_MA'] = data['Close'].rolling(window=slow_window).mean()

    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Initialize 'Position' column with zeros
    data['Position'] = 0

    # Define entry and exit conditions
    for i in range(1, len(data)):
        # If no position, check for entry signals
        if data['Position'].iloc[i - 1] == 0:
            # Long entry: Fast MA crosses above Slow MA and RSI is below overbought level
            if (data['Fast_MA'].iloc[i] > data['Slow_MA'].iloc[i]) and (data['Fast_MA'].iloc[i - 1] <= data['Slow_MA'].iloc[i - 1]) and (data['RSI'].iloc[i] < overbought):
                data.at[data.index[i], 'Position'] = 1  # Long position
            # Short entry: Fast MA crosses below Slow MA and RSI is above oversold level
            elif (data['Fast_MA'].iloc[i] < data['Slow_MA'].iloc[i]) and (data['Fast_MA'].iloc[i - 1] >= data['Slow_MA'].iloc[i - 1]) and (data['RSI'].iloc[i] > oversold):
                data.at[data.index[i], 'Position'] = -1  # Short position
        
        # Maintain position if already in one
        elif data['Position'].iloc[i - 1] == 1:
            # Close long if Fast MA crosses below Slow MA
            if data['Fast_MA'].iloc[i] < data['Slow_MA'].iloc[i]:
                data.at[data.index[i], 'Position'] = 0
            else:
                data.at[data.index[i], 'Position'] = 1  # Maintain long position

        elif data['Position'].iloc[i - 1] == -1:
            # Close short if Fast MA crosses above Slow MA
            if data['Fast_MA'].iloc[i] > data['Slow_MA'].iloc[i]:
                data.at[data.index[i], 'Position'] = 0
            else:
                data.at[data.index[i], 'Position'] = -1  # Maintain short position

    return data
