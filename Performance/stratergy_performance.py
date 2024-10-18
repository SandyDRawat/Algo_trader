import plotly.graph_objects as go
from Stratergy.sma_stratergy import sma_stratergy
from Stratergy.bb_stratergy import bb_stratergy
from Charts.candle_chart import interactive_candle_chart


def stratergy_performance(data, stratergy, start_date=None, end_date=None, initial_capital=10000):
    """
    Backtesting of a selected strategy over a specific date range.

    Parameters:
    - data: DataFrame with 'Close' price and strategy-specific columns
    - stratergy: Strategy name (e.g., 'sma', 'ema', 'bb', 'rsi', etc.)
    - start_date: Start date of the backtest in 'yyyy-mm-dd'. Default is the first date in the data.
    - end_date: End date of the backtest in 'yyyy-mm-dd'. Default is the last date in the data.
    - initial_capital: The initial amount of money for backtesting (default is 10,000)

    Returns:
    - Profit/Loss percentage and points captured by the strategy.
    """

    # Set default start and end dates if not provided
    if start_date is None:
        start_date = data.index.min()
    if end_date is None:
        end_date = data.index.max()

    # Filter data based on the selected date range
    data = data[(data.index >= start_date) & (data.index <= end_date)]
    
    # Apply the selected strategy
    if stratergy == 'sma':
        data = sma_stratergy(data)
 
    else:
        raise ValueError("Invalid strategy. Choose from 'sma', 'ema', 'bb', 'rsi', 'macd', 'atr', 'garman_klass'")
    
    """   elif stratergy == 'ema':
        data = ema_stratergy(data) 
    elif stratergy == 'bb':
        data = bb_stratergy(data)
    elif stratergy == 'rsi':
        data = rsi_stratergy(data)
    elif stratergy == 'macd':
        data = macd_stratergy(data)
    elif stratergy == 'atr':
        data = atr_stratergy(data)
    elif stratergy == 'garman_klass':
        data = garman_klass_stratergy(data)
    """
    print("Oh")
    print(data.head(30))
    print("Oh")
    fig = interactive_candle_chart(data, show_fig=True)
    
    # Calculate points captured by the strategy
    buy_prices = data.loc[data['Buy/Sell'] == 1, 'Close']
    sell_prices = data.loc[data['Buy/Sell'] == -1, 'Close']
    
    points_captured = sell_prices.sum() - buy_prices.sum()

    # Calculate profit/loss percentage
    capital = initial_capital
    position_size = 1  # Default number of shares

    for i in range(len(data)):
        if data['Buy/Sell'].iloc[i] == 1:  # Buy signal
            buy_price = data['Close'].iloc[i]
            shares = capital // buy_price  # Calculate how many shares we can buy
            capital -= shares * buy_price
            position_size = shares
        
        elif data['Buy/Sell'].iloc[i] == -1 and position_size > 0:  # Sell signal
            sell_price = data['Close'].iloc[i]
            capital += position_size * sell_price  # Sell all shares
            position_size = 0

    # Profit/Loss percentage calculation
    final_capital = capital + position_size * data['Close'].iloc[-1]  # Final value
    profit_loss_percentage = ((final_capital - initial_capital) / initial_capital) * 100

    return profit_loss_percentage, points_captured
