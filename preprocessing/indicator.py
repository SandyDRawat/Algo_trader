import numpy as np

def sma(data, period=14):
    """Simple Moving Average"""
    data['SMA'] = data['Close'].rolling(window=period).mean()
    return data

def ema(data, period=14):
    """Exponential Moving Average"""
    data['EMA'] = data['Close'].ewm(span=period, adjust=False).mean()
    return data

def rsi(data, period=14):
    """Relative Strength Index"""
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def bollinger_bands(data, period=20, num_std=2):
    """Bollinger Bands"""
    data['SMA'] = data['Close'].rolling(window=period).mean()
    data['STD'] = data['Close'].rolling(window=period).std()
    data['UpperBand'] = data['SMA'] + (data['STD'] * num_std)
    data['LowerBand'] = data['SMA'] - (data['STD'] * num_std)
    data.drop(columns=['STD'], inplace=True)
    return data

def macd(data, short_period=12, long_period=26, signal_period=9):
    """Moving Average Convergence Divergence"""
    short_ema = data['Close'].ewm(span=short_period, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_period, adjust=False).mean()
    data['MACD'] = short_ema - long_ema
    data['Signal'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
    return data

def atr(data, period=14):
    """Average True Range"""
    data['H-L'] = data['High'] - data['Low']
    data['H-PC'] = np.abs(data['High'] - data['Close'].shift(1))
    data['L-PC'] = np.abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=period).mean()
    data.drop(columns=['H-L', 'H-PC', 'L-PC', 'TR'], inplace=True)
    return data

def garman_klass(data):
    """Garman-Klass Volatility"""
    log_hl = np.log(data['High'] / data['Low']) ** 2
    log_oc = np.log(data['Open'] / data['Close']) ** 2
    data['GK'] = np.sqrt(0.5 * log_hl - (2 * np.log(2) - 1) * log_oc)
    return data
