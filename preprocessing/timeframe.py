import pandas as pd

def convert_timeframe(df, timeframe):
    """
    Convert stock price data from 1-minute timeframe to a desired timeframe.
    
    Parameters:
    - df: DataFrame containing stock price data with 'open', 'close', 'high', 'low', 'volume', and datetime index.
    - timeframe: A string representing the desired timeframe (e.g., '3T' for 3 minutes, '5T' for 5 minutes, 
                 '15T' for 15 minutes, '1H' for 1 hour, '1D' for 1 day, etc.).
    
    Returns:
    - A DataFrame resampled to the desired timeframe.
    """
    """
        Fill missing values in the DataFrame by averaging the values of the previous and next rows in the same column."""

    for col in df.columns:
        # Fill NaN values using the average of the previous and next row
        if df[col][1] is int:
            df[col] = df[col].fillna((df[col].shift(1) + df[col].shift(-1)) / 2)

   
    # Resample the data to the desired timeframe
    resampled_df = df.resample(timeframe).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    
    # Drop rows with missing data
    resampled_df.dropna(inplace=True)
    
    return resampled_df

# Example usage:
# Assuming you have a DataFrame `df` with a DateTime index and columns: 'open', 'high', 'low', 'close', 'volume'
# df.index should be in datetime format
# desired timeframe = '15T' for 15 minutes, '1H' for 1 hour, etc.
# df_resampled = convert_timeframe(df, '15T') 