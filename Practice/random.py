import random2
import pandas as pd

def randomdate_data(data):
    """
    Select a random date from the data and return data for the past week.
    
    Parameters:
    - data: DataFrame containing 'Open', 'High', 'Low', 'Close', 'Date', and 'Volume'.
    
    Returns:
    - selected_data: DataFrame with data for the past week including the selected date.
    - selected_date: The randomly selected date.
    """
    random_date = random2.choice(data.index)
    one_week_data = data.loc[random_date - pd.Timedelta(days=7):random_date]
    
    return one_week_data
