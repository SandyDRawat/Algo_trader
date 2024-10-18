import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd

# Load your actual data here
# Example DataFrame for demonstration purposes
df = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', periods=100),
    'Open': pd.Series(range(100)) + 1000,
    'High': pd.Series(range(100)) + 1010,
    'Low': pd.Series(range(100)) + 995,
    'Close': pd.Series(range(100)) + 1005,
    'Volume': pd.Series(range(100)) * 1000
})

app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Graph(id='candle-chart'),
    html.Button('Next Candle', id='next-btn', n_clicks=0),
    html.Button('Buy', id='buy-btn', n_clicks=0),
    html.Button('Sell', id='sell-btn', n_clicks=0),
    html.Div(id='trade-log', children='Trade Log:'),
])

# Initial empty DataFrame to keep track of trade actions
trade_df = pd.DataFrame(columns=['Date', 'Action', 'Price'])

# Callback to update the candlestick chart when "Next Candle" is clicked
@app.callback(
    Output('candle-chart', 'figure'),
    Input('next-btn', 'n_clicks')
)
def update_chart(n_clicks):
    num_candles_to_show = min(n_clicks + 10, len(df))
    
    # Generate a candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'][:num_candles_to_show],
        open=df['Open'][:num_candles_to_show],
        high=df['High'][:num_candles_to_show],
        low=df['Low'][:num_candles_to_show],
        close=df['Close'][:num_candles_to_show]
    )])
    
    return fig

# Callback to handle buy and sell actions
@app.callback(
    Output('trade-log', 'children'),
    [Input('buy-btn', 'n_clicks'), Input('sell-btn', 'n_clicks')],
    State('trade-log', 'children'),
    State('next-btn', 'n_clicks')
)
def handle_trade_actions(buy_clicks, sell_clicks, current_log, next_clicks):
    last_close_price = df.iloc[next_clicks]['Close']
    last_date = df.iloc[next_clicks]['Date']
    
    if buy_clicks > 0:
        current_log += f"\nBought at {last_close_price} on {last_date}"
    
    if sell_clicks > 0:
        current_log += f"\nSold at {last_close_price} on {last_date}"
    
    return current_log

if __name__ == '__main__':
    app.run_server(debug=True)
