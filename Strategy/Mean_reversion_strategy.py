import pandas as pd
import numpy as np

def mean_reversion_strategy(data, lookback=20):
    """
    Implements a mean reversion strategy.
    - Buy when the price falls significantly below the moving average (indicating an oversold condition).
    - Sell when the price rises significantly above the moving average (indicating an overbought condition).

    Parameters:
    - data: DataFrame with 'Close' prices.
    - lookback: Lookback period for calculating the moving average (default is 20).

    Returns:
    - DataFrame with added 'Moving Average' and 'Buy/Sell' columns.
    """
    # Calculate the moving average
    data['Moving Average'] = data['Close'].rolling(window=lookback).mean()

    # Calculate the deviation from the moving average
    data['Deviation'] = data['Close'] - data['Moving Average']

    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Buy when the price is significantly below the moving average
    data.loc[data['Deviation'] < -2 * data['Deviation'].std(), 'Buy/Sell'] = 1

    # Sell when the price is significantly above the moving average
    data.loc[data['Deviation'] > 2 * data['Deviation'].std(), 'Buy/Sell'] = -1

    return data
import pandas as pd
import numpy as np

def mean_reversion_strategy(data, lookback=20):
    """
    Implements a mean reversion strategy.
    - Buy when the price falls significantly below the moving average (indicating an oversold condition).
    - Sell when the price rises significantly above the moving average (indicating an overbought condition).

    Parameters:
    - data: DataFrame with 'Close' prices.
    - lookback: Lookback period for calculating the moving average (default is 20).

    Returns:
    - DataFrame with added 'Moving Average' and 'Buy/Sell' columns.
    """
    # Calculate the moving average
    data['Moving Average'] = data['Close'].rolling(window=lookback).mean()

    # Calculate the deviation from the moving average
    data['Deviation'] = data['Close'] - data['Moving Average']

    # Initialize 'Buy/Sell' column with zeros
    data['Buy/Sell'] = 0

    # Buy when the price is significantly below the moving average
    data.loc[data['Deviation'] < -2 * data['Deviation'].std(), 'Buy/Sell'] = 1

    # Sell when the price is significantly above the moving average
    data.loc[data['Deviation'] > 2 * data['Deviation'].std(), 'Buy/Sell'] = -1

    return data
