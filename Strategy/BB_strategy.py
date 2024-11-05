from preprocessing.indicator import bollinger_bands

'''def bollinger_band_strategy(data):
    """
    Implements a Bollinger Bands trading strategy using a Position column.
    Adds a 'Position' column where:
    - 1 indicates holding a long position (price is below the lower band and expected to rise).
    - -1 indicates holding a short position (price is above the upper band and expected to fall).
    - 0 indicates no position (position closed).

    Parameters:
    - data: DataFrame with 'Close' price, pre-calculated 'UpperBand' and 'LowerBand'.

    Returns:
    - DataFrame with an added 'Position' column.
    """
    # Ensure the necessary columns exist in the data
    
    if 'UpperBand' not in data.columns or 'LowerBand' not in data.columns:
        data = bollinger_bands(data, period=20, num_std=2)
    
    # Make a copy of the data to prevent SettingWithCopyWarning
    data = data.copy()
    
    # Initialize 'Position' column with zeros (no position)
    data['Position'] = 0

    # Define the conditions for entering and exiting positions
    for i in range(1, len(data)):
        # If no position, check for entry signals
        if data['Position'].iloc[i - 1] == 0:
            # Enter a long position if low  crosses below the Lower Band
            if data['Low'].iloc[i] >= data['LowerBand'].iloc[i] and data['Low'].iloc[i - 1] <= data['LowerBand'].iloc[i - 1]:
                data.at[data.index[i], 'Position'] = 1  # Long position
                stoploss = 0.95*data['Open'].iloc[i]
            # Enter a short position if Close crosses above the Upper Band
            elif data['High'].iloc[i] <= data['UpperBand'].iloc[i] and data['High'].iloc[i - 1] >= data['UpperBand'].iloc[i - 1]:
                data.at[data.index[i], 'Position'] = -1  # Short position
                stoploss = 1.05*data['Open'].iloc[i]
        # If holding a long position, check if it should be closed or maintained
        elif data['Position'].iloc[i - 1] == 1:
            # Close long if price returns above Lower Band
            if data['Close'].iloc[i] >= data['UpperBand'].iloc[i]:
                stoploss = data['Open'].iloc[i-1]  # Close long position
                data.at[data.index[i], 'Position'] = 1
            elif data['Close'].iloc[i] <= stoploss:
                data.at[data.index[i], 'Position'] = 0  # Close long position
            else:
                data.at[data.index[i], 'Position'] = 1  # Maintain long position

        # If holding a short position, check if it should be closed or maintained
        elif data['Position'].iloc[i - 1] == -1:
            # Close short if price returns below Upper Band
            if data['Close'].iloc[i] <= data['LowerBand'].iloc[i]:
                stoploss = data['Open'].iloc[i-1]  # Close short position
                data.at[data.index[i], 'Position'] = -1
            elif data['Close'].iloc[i] >= stoploss:
                data.at[data.index[i], 'Position'] = 0
            else:
                data.at[data.index[i], 'Position'] = -1  # Maintain short position

    return data

from preprocessing.indicator import bollinger_bands'''

def bollinger_band_strategy(data):
    """
    Implements a simple Bollinger Bands trading strategy using a Position column.
    Adds a 'Position' column where:
    - 1 indicates holding a long position (price is below the lower band and expected to rise).
    - -1 indicates holding a short position (price is above the upper band and expected to fall).
    - 0 indicates no position (position closed).

    Parameters:
    - data: DataFrame with 'Close' price, pre-calculated 'UpperBand' and 'LowerBand'.

    Returns:
    - DataFrame with an added 'Position' column.
    """
    # Ensure the necessary columns exist in the data
    if 'UpperBand' not in data.columns or 'LowerBand' not in data.columns:
        data = bollinger_bands(data, period=20, num_std=2)
    
    # Make a copy of the data to prevent SettingWithCopyWarning
    data = data.copy()
    
    # Initialize 'Position' column with zeros (no position)
    data['Position'] = 0

    # Define the conditions for entering and exiting positions
    for i in range(1, len(data)):
        # If no position, check for entry signals
        if data['Position'].iloc[i - 1] == 0:
            # Enter a long position if the Close crosses below the Lower Band
            if data['Close'].iloc[i] < data['LowerBand'].iloc[i]:
                data.at[data.index[i], 'Position'] = 1  # Long position
            # Enter a short position if the Close crosses above the Upper Band
            elif data['Close'].iloc[i] > data['UpperBand'].iloc[i]:
                data.at[data.index[i], 'Position'] = -1  # Short position

        # If holding a long position, check if it should be closed
        elif data['Position'].iloc[i - 1] == 1:
            # Close long if price rises back above the Lower Band
            if data['Close'].iloc[i] > data['LowerBand'].iloc[i]:
                data.at[data.index[i], 'Position'] = 0  # Close long position

        # If holding a short position, check if it should be closed
        elif data['Position'].iloc[i - 1] == -1:
            # Close short if price falls back below the Upper Band
            if data['Close'].iloc[i] < data['UpperBand'].iloc[i]:
                data.at[data.index[i], 'Position'] = 0  # Close short position

    return data
