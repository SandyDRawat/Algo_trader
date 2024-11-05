from preprocessing.indicator import rsi

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
    data = rsi(data)

    # Initialize 'Buy/Sell' column with zeros
    data['Position'] = 0

    # Buy RSI is below the oversold threshold
    data.loc[data['RSI'] < rsi_oversold, 'Position'] = 1

    # Sell when RSI is above the overbought threshold
    data.loc[data['RSI'] > rsi_overbought, 'Position'] = -1

    return data
