import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from preprocessing.cleaning import data_cleaning
from Charts.candle_chart import interactive_candle_chart

def plotter(selected_data):
    """
    Plot the selected data and allow for dynamic updates using a 'next' button and buy/sell markers.
    
    Parameters:
    - selected_data: DataFrame containing 'Open', 'High', 'Low', 'Close', 'Date', 'Volume', and indicators.
    
    Returns:
    - updated_data: DataFrame with additional buy/sell actions added during interaction.
    """
    
    # Make sure 'Date' column is in datetime format and set as index
    if not isinstance(selected_data.index, pd.DatetimeIndex):
        selected_data['Date'] = pd.to_datetime(selected_data['Date'])
        selected_data.set_index('Date', inplace=True)

    # Store initial selected data and state for "next" functionality
    data_copy = selected_data.copy()
    current_index = len(data_copy)
    full_data = selected_data.copy()

    # Call the existing candle_chart function to create the base plot
    fig = interactive_candle_chart(data_copy, show_fig=False)

    # Initialize traces for updating
    candlestick_trace = fig.data[0]  # Assuming the candlestick trace is the first trace in fig.data

    # Add buy and sell buttons
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(label="Next Candle",
                         method="update",
                         args=[{'visible': True},
                               dict()]),  # Placeholder, this will call the update function
                    dict(label="Buy",
                         method="update",
                         args=[{'visible': True},
                               dict()]),  # Buy button action
                    dict(label="Sell",
                         method="update",
                         args=[{'visible': True},
                               dict()]),  # Sell button action
                ],
                direction="left",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.15,
                yanchor="top"
            )
        ]
    )

    # Callback to update the chart with the next candle (without changing the layout)
    def update_next_candle():
        nonlocal current_index, data_copy, candlestick_trace
        if current_index < len(full_data):
            next_candle = full_data.iloc[current_index:current_index + 1]
            current_index += 1
            data_copy = pd.concat([data_copy, next_candle])
            candlestick_trace.x = data_copy.index
            candlestick_trace.open = data_copy['Open']
            candlestick_trace.high = data_copy['High']
            candlestick_trace.low = data_copy['Low']
            candlestick_trace.close = data_copy['Close']
    
    # Add buy/sell actions to the data
    def add_buy_sell_action(action):
        price = data_copy.iloc[-1]['Close']
        time = data_copy.index[-1]
        data_copy.loc[time, 'Buy/Sell'] = 1 if action == 'buy' else -1

        # Add the marker to the chart for buy/sell
        marker_symbol = 'triangle-up' if action == 'buy' else 'triangle-down'
        marker_color = 'green' if action == 'buy' else 'red'
        fig.add_trace(go.Scatter(
            x=[time], y=[price],
            mode='markers',
            marker=dict(symbol=marker_symbol, color=marker_color, size=10),
            name="Buy Signal" if action == 'buy' else "Sell Signal"
        ))

    # Map button actions to functions
    def button_callbacks(button_name):
        if button_name == "Next Candle":
            update_next_candle()
        elif button_name == "Buy":
            add_buy_sell_action('buy')
        elif button_name == "Sell":
            add_buy_sell_action('sell')

    # Bind button actions with click event
    for button in fig.layout.updatemenus[0]['buttons']:
        button['args'] = [None, {"callback": lambda: button_callbacks(button['label'])}]
    
    # Show the chart with interactive options
    fig.show()

    return data_copy
