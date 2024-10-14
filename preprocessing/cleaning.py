import pandas as pd

def data_cleaning(data):
   
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)

    column_mapping = {
        'date': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    data = data.rename(columns=column_mapping)

    return data
# Example usage:
# cleaned_data = data_cleaning(data)
