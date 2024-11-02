from preprocessing.indicator import sma, ema, rsi, macd, bollinger_bands, atr, garman_klass

def convert_timeframe(df, timeframe):
    """
    Convert stock price data from 1-minute timeframe to a desired timeframe and reapply indicators.
    
    Parameters:
    - df: DataFrame containing stock price data with 'open', 'close', 'high', 'low', 'volume', and datetime index.
    - timeframe: A string representing the desired timeframe (e.g., '3T' for 3 minutes, '5T' for 5 minutes, 
                 '15T' for 15 minutes, '1H' for 1 hour, '1D' for 1 day, etc.).
    
    Returns:
    - A DataFrame resampled to the desired timeframe with updated indicators.
    """
    # Fill missing values in the DataFrame by averaging the values of the previous and next rows in the same column
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
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

    # Handle Buy/Sell signals: Keep first or last signal in each timeframe
    if 'Buy/Sell' in df.columns:
        resampled_df['Buy/Sell'] = df['Buy/Sell'].resample(timeframe).last()  # or .first(), depending on your logic

    # Reapply indicators for the new timeframe
    if 'SMA' in df.columns:
        resampled_df = sma(resampled_df)
    if 'EMA' in df.columns:
        resampled_df = ema(resampled_df)
    if 'RSI' in df.columns:
        resampled_df = rsi(resampled_df)  # Recalculate RSI on the resampled close prices
    if 'MACD' in df.columns:
        resampled_df = macd(resampled_df)
    if 'UpperBand' in df.columns and 'LowerBand' in df.columns:
        resampled_df=  bollinger_bands(resampled_df)
    if 'ATR' in df.columns:
        resampled_df = atr(resampled_df)
    if 'GK' in df.columns:
        resampled_df = garman_klass(resampled_df)

    return resampled_df
