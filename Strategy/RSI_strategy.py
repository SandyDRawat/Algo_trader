import pandas as pd
import numpy as np

def rsi_strategy(data, rsi_period=14, rsi_overbought=70, rsi_oversold=30):
    """
    Implements a simple RSI-based strategy.
    - Buy when RSI is below the oversold threshold.
    - Sell when RSI is above the overbought threshold.

    Parameters:
    - data: DataFrame with 'Close' prices.
    - rsi_period: Period for RSI calculation (default is 14).
    - rsi_overbought: RSI level considered as overbought (default is 70).
    - rsi_oversold: RSI level considered as oversold (default is 30).

    Returns:
    - DataFrame with added 'RSI' and 'Buy/Sell' columns.
    """
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Buy when RSI is below the oversold threshold
    data.loc[data['RSI'] < rsi_oversold, 'Buy/Sell'] = 1

    # Sell when RSI is above the overbought threshold
    data.loc[data['RSI'] > rsi_overbought, 'Buy/Sell'] = -1

    return data
