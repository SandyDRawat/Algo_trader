def performance(after_practice_data):
    """
    Calculate the performance metrics (PnL, returns) from the buy/sell actions in the data.
    
    Parameters:
    - after_practice_data: DataFrame containing buy/sell signals and prices.
    
    Returns:
    - results: Dictionary with total PnL, total returns, and number of trades.
    """
    buy_sell_data = after_practice_data.dropna(subset=['Buy/Sell'])
    
    pnl = 0
    trades = 0
    for i in range(1, len(buy_sell_data)):
        current_signal = buy_sell_data['Buy/Sell'].iloc[i-1]
        next_signal = buy_sell_data['Buy/Sell'].iloc[i]
        if current_signal == 1 and next_signal == -1:  # Buy -> Sell
            pnl += buy_sell_data['Close'].iloc[i] - buy_sell_data['Close'].iloc[i-1]
            trades += 1
    
    total_returns = pnl / buy_sell_data['Close'].iloc[0] * 100  # Percentage returns

    results = {
        'PnL': pnl,
        'Returns': total_returns,
        'Trades': trades
    }
    return results
