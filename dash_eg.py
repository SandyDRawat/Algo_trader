import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from preprocessing.timeframe import convert_timeframe

# Create a sample DataFrame (replace this with your actual data)
data = pd.DataFrame({
    'Date': pd.date_range(start='2021-01-01', periods=100, freq='1T'),
    'Open': pd.np.random.randn(100).cumsum(),
    'High': pd.np.random.randn(100).cumsum(),
    'Low': pd.np.random.randn(100).cumsum(),
    'Close': pd.np.random.randn(100).cumsum(),
    'Buy/Sell': [1 if x % 10 == 0 else -1 if x % 15 == 0 else 0 for x in range(100)]
})

# Convert the Date column to datetime
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive Candlestick Chart with Dash"),
    
    # Dropdown for timeframes
    dcc.Dropdown(
        id='timeframe-dropdown',
        options=[
            {'label': '1 Minute', 'value': '1min'},
            {'label': '5 Minutes', 'value': '5min'}
        ],
        value='1min',
        clearable=False
    ),
    
    # Graph for candlestick chart
    dcc.Graph(id='candlestick-chart')
])

# Update the chart based on the selected timeframe
@app.callback(
    Output('candlestick-chart', 'figure'),
    [Input('timeframe-dropdown', 'value')]
)
def update_candlestick_chart(timeframe):
    # Convert data based on selected timeframe
    new_data = convert_timeframe(data, timeframe)
    
    # Create a new candlestick figure
    fig = go.Figure(data=[go.Candlestick(x=new_data.index,
                                         open=new_data['Open'],
                                         high=new_data['High'],
                                         low=new_data['Low'],
                                         close=new_data['Close'],
                                         name="Candlestick")])
    
    # Add Buy/Sell signals if available
    if 'Buy/Sell' in new_data.columns:
        buy_signals = new_data[new_data['Buy/Sell'] == 1]
        sell_signals = new_data[new_data['Buy/Sell'] == -1]
        
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers',
                                 marker=dict(symbol="triangle-up", color="green", size=10),
                                 name="Buy Signal"))
        
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers',
                                 marker=dict(symbol="triangle-down", color="red", size=10),
                                 name="Sell Signal"))
    
    # Customize layout
    fig.update_layout(
        title=f"Candlestick Chart ({timeframe})",
        xaxis_title='Date',
        yaxis_title='Price',
        hovermode='x unified',
        dragmode='zoom',
        xaxis_rangeslider_visible=False,
        xaxis=dict(showgrid=True, gridcolor='LightGrey', gridwidth=1),
        yaxis=dict(showgrid=True, gridcolor='LightGrey', gridwidth=1)
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
