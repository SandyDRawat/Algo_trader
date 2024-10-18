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

    # Function to update the chart with buy/sell markers (if 'Buy/Sell' exists)
    def update_chart_wpts(timeframe):
        # Convert data to selected timeframe using the updated convert_timeframe function
        new_data = convert_timeframe(data, timeframe)

        # Update candlestick traces
        traces = {
            'open': new_data['Open'],
            'high': new_data['High'],
            'low': new_data['Low'],
            'close': new_data['Close'],
            'x': new_data.index
        }

        # Check if 'Buy/Sell' column exists in the new data
        if 'Buy/Sell' in new_data.columns:
            # Extract buy and sell signals from 'Buy/Sell' column in new_data
            buy_signals = new_data[new_data['Buy/Sell'] == 1]
            sell_signals = new_data[new_data['Buy/Sell'] == -1]

            # Create traces for buy/sell markers
            buy_trace = go.Scatter(
                x=buy_signals.index,
                y=buy_signals['Close'],
                marker=dict(symbol="triangle-up", color="green", size=10),
                mode='markers',
                name='Buy Signal'
            )

            sell_trace = go.Scatter(
                x=sell_signals.index,
                y=sell_signals['Close'],
                marker=dict(symbol="triangle-down", color="red", size=10),
                mode='markers',
                name='Sell Signal'
            )
        else:
            # If 'Buy/Sell' column does not exist, return empty traces
            buy_trace = sell_trace = None

        # Reapply indicators based on the resampled data
        indicators = []
        for col in new_data.columns:
            if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Buy/Sell']:
                indicators.append(go.Scatter(
                    x=new_data.index,
                    y=new_data[col],
                    mode='lines',
                    name=col,
                    yaxis='y2' if col == 'RSI' else 'y'
                ))

        return traces, indicators, buy_trace, sell_trace

    # Function to update the chart without buy/sell markers
    def update_chart(timeframe):
        # Convert data to selected timeframe using provided function
        new_data = convert_timeframe(data, timeframe)

        # Update candlestick traces
        traces = {
            'open': new_data['Open'],
            'high': new_data['High'],
            'low': new_data['Low'],
            'close': new_data['Close'],
            'x': new_data.index
        }

        # Collect indicator values
        indicators = []
        for col in indicator_columns:
            if col in new_data.columns:
                indicators.append(go.Scatter(
                    x=new_data.index,
                    y=new_data[col],
                    mode='lines',
                    name=col,
                    yaxis='y2' if col == 'RSI' else 'y'
                ))

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
                        args=[
                            {'x': [update_chart_wpts("1min")[0]['x']] if buy_sell_exists else [update_chart("1min")[0]['x']],
                             'open': [update_chart_wpts("1min")[0]['open']] if buy_sell_exists else [update_chart("1min")[0]['open']],
                             'high': [update_chart_wpts("1min")[0]['high']] if buy_sell_exists else [update_chart("1min")[0]['high']],
                             'low': [update_chart_wpts("1min")[0]['low']] if buy_sell_exists else [update_chart("1min")[0]['low']],
                             'close': [update_chart_wpts("1min")[0]['close']] if buy_sell_exists else [update_chart("1min")[0]['close']]},
                            update_chart_wpts("1min")[1] if buy_sell_exists else update_chart("1min")[1]
                        ]
                    ),
                    dict(
                        label="5 Min",
                        method="update",
                        args=[
                            {'x': [update_chart_wpts("5min")[0]['x']] if buy_sell_exists else [update_chart("5min")[0]['x']],
                             'open': [update_chart_wpts("5min")[0]['open']] if buy_sell_exists else [update_chart("5min")[0]['open']],
                             'high': [update_chart_wpts("5min")[0]['high']] if buy_sell_exists else [update_chart("5min")[0]['high']],
                             'low': [update_chart_wpts("5min")[0]['low']] if buy_sell_exists else [update_chart("5min")[0]['low']],
                             'close': [update_chart_wpts("5min")[0]['close']] if buy_sell_exists else [update_chart("5min")[0]['close']]},
                            update_chart_wpts("5min")[1] if buy_sell_exists else update_chart("5min")[1]
                        ]
                    ),
                ],
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.05,
                yanchor="top"
            )
        ]
    )

    if show_fig:
        fig.show()

    return fig