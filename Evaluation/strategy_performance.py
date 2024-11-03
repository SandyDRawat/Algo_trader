from Strategy.SMA_strategy import sma_strategy
from Strategy.BB_strategy import bollinger_band_strategy
from Charts.candle_chart import interactive_candle_chart
from Strategy.Intraday_gap_strategy import intraday_gap_strategy
from Strategy.RSI_strategy import rsi_strategy
from Strategy.MACD_crossover_strategy import macd_strategy
from Strategy.Mean_reversion_strategy import mean_reversion_strategy
from Strategy.Trend_following_breakout_strategy import breakout_strategy

def strategy_performance(data, strategy, start_date=None, end_date=None, initial_capital=10000):
    """
    Backtesting of a selected strategy over a specific date range with support for long and short positions.

    Parameters:
    - data: DataFrame with 'Close' price and strategy-specific columns.
    - strategy: Strategy name (e.g., 'sma', 'bb', 'rsi', 'macd', 'idg', etc.).
    - start_date: Start date of the backtest in 'yyyy-mm-dd'. Default is the first date in the data.
    - end_date: End date of the backtest in 'yyyy-mm-dd'. Default is the last date in the data.
    - initial_capital: The initial amount of money for backtesting (default is 10,000).

    Returns:
    - Final capital, Profit/Loss percentage, and points captured by the strategy.
    """

    # Set default start and end dates if not provided
    if start_date is None:
        start_date = data.index.min()
    if end_date is None:
        end_date = data.index.max()

    # Filter data based on the selected date range
    data = data[(data.index >= start_date) & (data.index <= end_date)]

    # Apply the selected strategy
    if strategy == 'sma':
        data = sma_strategy(data)
    elif strategy == 'bb':
        data = bollinger_band_strategy(data)
    elif strategy == 'rsi':
        data = rsi_strategy(data)
    elif strategy == 'macd':
        data = macd_strategy(data)
    elif strategy == 'idg':
        data = intraday_gap_strategy(data)
    elif strategy == 'tfb':
        data = breakout_strategy(data)
    elif strategy == 'mr':
        data = mean_reversion_strategy(data)
    else:
        raise ValueError("Invalid strategy. Choose from 'sma', 'bb', 'rsi', 'macd', 'idg', 'tfb', 'mr'")

    # Display interactive chart
    fig = interactive_candle_chart(data, show_fig=True)

    # Initialize capital and position tracking
    capital = initial_capital
    position = 0  # Tracks the number of shares in long or short
    entry_price = 0  # Tracks the price at which position was entered
    points_captured = 0

    # Evaluate performance based on Position changes
    for i in range(1, len(data)):
        # Check for position change
        if data['Position'].iloc[i] != data['Position'].iloc[i - 1]:
            # Closing an existing position (either long or short)
            if position != 0:
                exit_price = data['Close'].iloc[i]
                if position > 0:  # Long position
                    profit = (exit_price - entry_price) * position
                elif position < 0:  # Short position
                    profit = (entry_price - exit_price) * abs(position)
                
                capital += profit
                points_captured += profit
                position = 0  # Reset position after closing

            # Entering a new position (long or short)
            if data['Position'].iloc[i] == 1:  # Enter long position
                entry_price = data['Close'].iloc[i]
                position = capital // entry_price  # Buy as many shares as possible
                capital -= position * entry_price  # Deduct cost of shares

            elif data['Position'].iloc[i] == -1:  # Enter short position
                entry_price = data['Close'].iloc[i]
                position = - (capital // entry_price)  # Short as many shares as possible

    # Final capital after closing any open positions at the last price
    final_capital = capital + (position * data['Close'].iloc[-1])
    profit_loss_percentage = ((final_capital - initial_capital) / initial_capital) * 100

    return final_capital, profit_loss_percentage, points_captured
