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

    # Ensure 'Date' column is in datetime format and set as index
    if not isinstance(data.index, pd.DatetimeIndex):
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)

    # Default timeframe is the current data
    current_data = data.copy()

    # Collect indicator columns from the data
    indicator_columns = [col for col in data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume','Buy/Sell']]

    # Create the initial candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=current_data.index,
                                         open=current_data['Open'],
                                         high=current_data['High'],
                                         low=current_data['Low'],
                                         close=current_data['Close'],
                                         name="Candlestick")])

    # Add buy and sell markers from the 'Buy/Sell' column
    if 'Buy/Sell' in current_data.columns:
        buy_signals = current_data[current_data['Buy/Sell'] == 1]
        sell_signals = current_data[current_data['Buy/Sell'] == -1]

        # Add buy (green triangle up) and sell (red triangle down) markers
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers',
                                 marker=dict(symbol="triangle-up", color="green", size=10),
                                 name="Buy Signal"))

        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers',
                                 marker=dict(symbol="triangle-down", color="red", size=10),
                                 name="Sell Signal"))

    # Add indicators as line charts; plot RSI on a secondary y-axis if it exists
    for indicator in indicator_columns:
        if indicator in current_data.columns:
            if indicator == 'RSI':
                fig.add_trace(go.Scatter(x=current_data.index, y=current_data[indicator], mode='lines', name=indicator,
                                         yaxis='y2'))
            else:
                fig.add_trace(go.Scatter(x=current_data.index, y=current_data[indicator], mode='lines', name=indicator))

    # Function to update the chart with a new timeframe
    def update_chart(timeframe):
        # Convert data to selected timeframe using provided function
        new_data = convert_timeframe(data, timeframe)
        traces = {
            'open': new_data['Open'], 
            'high': new_data['High'], 
            'low': new_data['Low'], 
            'close': new_data['Close'], 
            'x': new_data.index
        }
        # Collect all indicators, only if they exist in the new_data
        indicators = {col: new_data[col] for col in indicator_columns if col in new_data.columns}
        return traces, indicators

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
        )
    )

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
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="1 Min",
                        method="update",
                        args=[{'x': [update_chart("1min")[0]['x']],
                               'open': [update_chart("1min")[0]['open']],
                               'high': [update_chart("1min")[0]['high']],
                               'low': [update_chart("1min")[0]['low']],
                               'close': [update_chart("1min")[0]['close']]},
                              [{'x': update_chart("1min")[0]['x'], 'y': update_chart("1min")[1].get(col, []), 'yaxis': 'y2' if col == 'RSI' else 'y'} for col in indicator_columns]],
                    ),
                    dict(
                        label="5 Min",
                        method="update",
                        args=[{'x': [update_chart("5min")[0]['x']],
                               'open': [update_chart("5min")[0]['open']],
                               'high': [update_chart("5min")[0]['high']],
                               'low': [update_chart("5min")[0]['low']],
                               'close': [update_chart("5min")[0]['close']]},
                              [{'x': update_chart("5min")[0]['x'], 'y': update_chart("5min")[1].get(col, []), 'yaxis': 'y2' if col == 'RSI' else 'y'} for col in indicator_columns]],
                    ),
                    dict(
                        label="10 Min",
                        method="update",
                        args=[{'x': [update_chart("10min")[0]['x']],
                               'open': [update_chart("10min")[0]['open']],
                               'high': [update_chart("10min")[0]['high']],
                               'low': [update_chart("10min")[0]['low']],
                               'close': [update_chart("10min")[0]['close']]},
                              [{'x': update_chart("10min")[0]['x'], 'y': update_chart("10min")[1].get(col, []), 'yaxis': 'y2' if col == 'RSI' else 'y'} for col in indicator_columns]],
                    ),
                    dict(
                        label="15 Min",
                        method="update",
                        args=[{'x': [update_chart("15min")[0]['x']],
                               'open': [update_chart("15min")[0]['open']],
                               'high': [update_chart("15min")[0]['high']],
                               'low': [update_chart("15min")[0]['low']],
                               'close': [update_chart("15min")[0]['close']]},
                              [{'x': update_chart("15min")[0]['x'], 'y': update_chart("15min")[1].get(col, []), 'yaxis': 'y2' if col == 'RSI' else 'y'} for col in indicator_columns]],
                    ),
                    dict(
                        label="1 Hour",
                        method="update",
                        args=[{'x': [update_chart("1h")[0]['x']],
                               'open': [update_chart("1h")[0]['open']],
                               'high': [update_chart("1h")[0]['high']],
                               'low': [update_chart("1h")[0]['low']],
                               'close': [update_chart("1h")[0]['close']]},
                              [{'x': update_chart("1h")[0]['x'], 'y': update_chart("1h")[1].get(col, []), 'yaxis': 'y2' if col == 'RSI' else 'y'} for col in indicator_columns]],
                    )
                ],
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.5,  # Center horizontally
                xanchor="center",
                y=-0.4,  # Below the chart
                yanchor="bottom"
            )
        ]
    )

    # Show the chart       
    if show_fig:
        fig.show() 
    return fig
