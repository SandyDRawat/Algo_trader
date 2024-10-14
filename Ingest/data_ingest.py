import pandas as pd

def data_in_csv(data_path):
    data = pd.read_csv(data_path)
    return data