import random2
import pandas as pd

def randomdate_data(data):
    """
    Select a random date from the data, ensuring the trading day starts at 9:15 AM,
    and return data for the past week.
    
    Parameters:
    - data: DataFrame containing 'Open', 'High', 'Low', 'Close', 'Date', and 'Volume',
            with a datetime index.
    
    Returns:
    - selected_data: DataFrame with data for the past week including the selected date.
    """
    # Filter data to include only rows that start at 9:15 AM
    trading_days = data.between_time('09:15', '09:15').index
    random_date = random2.choice(trading_days)
    
    # Get the data for the past week ending on the selected date
    one_week_data = data.loc[random_date - pd.Timedelta(days=7):random_date]
    
    return one_week_data
