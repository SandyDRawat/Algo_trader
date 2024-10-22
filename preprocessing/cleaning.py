import pandas as pd

def data_cleaning(data):
    start_time = "09:15"
    end_time = "15:30"

    # Convert 'date' column to datetime if not already in DateTime format
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])


    # Rename columns to match a consistent format
    column_mapping = {
        'date': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    data = data.rename(columns=column_mapping)

    # Ensure 'date' is set as the index
    data.set_index('Date', inplace=True)

    # Remove any rows with missing data
    data.dropna(inplace=True)

    # Filter data to only include rows within the trading hours
    filtered_data = data.between_time(start_time, end_time)

    return filtered_data
