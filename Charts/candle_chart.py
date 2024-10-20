import pandas as pd
import plotly.graph_objects as go
from preprocessing.timeframe import convert_timeframe

def interactive_candle_chart(data, show_fig=True):
    """
    Create an interactive candlestick chart with Plotly that includes drawing tools, zoom slider,
    crosshair cursor, gridlines, indicators, and time interval selection.

    Parameters:
    - data: DataFrame containing 'Open', 'High', 'Low', 'Close', 'Date', and optional indicator columns.
    """
    # Check if 'Buy/Sell' column is present
    buy_sell_exists = 'Buy/Sell' in data.columns

    # Ensure 'Date' column is in datetime format and set as index
    if not isinstance(data.index, pd.DatetimeIndex):
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)

    # Collect indicator columns from the data
    indicator_columns = [col for col in data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Buy/Sell']]

    # Create the initial candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'],
                                         name="Candlestick")])

    # Add buy and sell markers from the 'Buy/Sell' column if it exists
    if buy_sell_exists:
        buy_signals = data[data['Buy/Sell'] == 1]
        sell_signals = data[data['Buy/Sell'] == -1]

        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers',
                                 marker=dict(symbol="triangle-up", color="green", size=10),
                                 name="Buy Signal"))

        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers',
                                 marker=dict(symbol="triangle-down", color="red", size=10),
                                 name="Sell Signal"))

    # Add indicators as line charts; plot RSI on a secondary y-axis if it exists
    for indicator in indicator_columns:
        if indicator == 'RSI':
            fig.add_trace(go.Scatter(x=data.index, y=data[indicator], mode='lines', name=indicator,
                                     yaxis='y2'))
        else:
            fig.add_trace(go.Scatter(x=data.index, y=data[indicator], mode='lines', name=indicator))
   

    # Customize layout to include crosshair, gridlines, and drawing tools
    fig.update_layout(
        title='Interactive Candlestick Chart with Features',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,  # Disable the horizontal slider (range slider)
        hovermode='x unified',  # Crosshair cursor
        dragmode='zoom',  # Default mode allows zooming
        xaxis=dict(showgrid=True, gridcolor='LightGrey', gridwidth=1),  # X-axis gridlines
        yaxis=dict(showgrid=True, gridcolor='LightGrey', gridwidth=1),  # Y-axis gridlines
        yaxis2=dict(
            title='RSI',
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, 100]  # RSI usually ranges from 0 to 100
        ))
    

    fig.update_xaxes(rangebreaks=[dict(bounds=[16, 9], pattern="hour"),
                              dict(bounds=['sat', 'mon'])
                              ])
    

    # Add buttons for drawing tools, zoom, pan, and eraser
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(args=["dragmode", "drawline"], label="Draw Line", method="relayout"),
                    dict(args=["dragmode", "drawrect"], label="Draw Rectangle", method="relayout"),
                    dict(args=["dragmode", "drawcircle"], label="Draw Circle", method="relayout"),
                    dict(args=["dragmode", "pan"], label="Pan", method="relayout"),
                    dict(args=["dragmode", "zoom"], label="Zoom", method="relayout"),
                    dict(args=[{"shapes": []}], label="Erase All", method="relayout"),
                ],
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.5,  # Center horizontally
                xanchor="center",
                y=1.2,  # Above the chart
                yanchor="top"
            ),
            
            
        ]
    )

    if show_fig:
        fig.show()

    return fig