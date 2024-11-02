from Strategy.SMA_strategy import sma_strategy
from Strategy.BB_strategy import bollinger_band_strategy
from Charts.candle_chart import interactive_candle_chart
from Strategy.Intraday_gap_strategy import intraday_gap_strategy
from Strategy.RSI_strategy import rsi_strategy
from Strategy.MACD_crossover_strategy import macd_strategy
from Strategy.Mean_reversion_strategy import mean_reversion_strategy
from Strategy.Trend_following_breakout_strategy import breakout_strategy


def strategy_performance(data, stratrgy, start_date=None, end_date=None, initial_capital=10000):
    """
    Backtesting of a selected strategy over a specific date range.

    Parameters:
    - data: DataFrame with 'Close' price and strategy-specific columns
    - stratrgy: Strategy name (e.g., 'sma', 'ema', 'bb', 'rsi', etc.)
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
    if stratrgy == 'sma':
        data = sma_strategy(data)
    elif stratrgy == 'bb':
        data = bollinger_band_strategy(data)
    elif stratrgy == 'rsi':
        data = rsi_strategy(data)
    elif stratrgy == 'macd':
        data = macd_strategy(data)
    elif stratrgy == 'idg':
        data = intraday_gap_strategy(data)
    elif stratrgy == 'tfb':
        data = breakout_strategy(data)
    elif stratrgy == 'mr':
        data = mean_reversion_strategy(data)
    else:
        raise ValueError("Invalid strategy. Choose from 'sma', 'bb', 'rsi', 'macd', 'idg', 'tfb', 'mr'")
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

    return final_capital,profit_loss_percentage, points_captured
