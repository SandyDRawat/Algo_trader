import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from Ingest.data_ingest import data_in_csv  # Assuming the function is inside this module
from preprocessing.cleaning import data_cleaning  # Assuming the cleaning logic is in this module
from preprocessing.timeframe import convert_timeframe
from indicators.indicator import sma, ema, rsi  # Using only a few indicators for simplicity

# Initialize Dash App
app = dash.Dash(__name__)

# Filepath to the dataset
file_path = 'data/NIFTY50-Minute_data.csv'

# Load and prepare the data
data = data_cleaning(data_in_csv(file_path)).head(5000)  # Using a larger dataset for testing
data = sma(data)
data = ema(data)
data = rsi(data)

# Collect available timeframes and indicators
available_timeframes = ['1min', '5min', '15min', '30min', '1h']
indicators = [col for col in data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Date']]

# Define Layout of the Dash App
app.layout = html.Div([
    html.H1('Interactive Candlestick Chart with Dash'),

    # Dropdown to select timeframes
    dcc.Dropdown(
        id='timeframe-selector',
        options=[{'label': timeframe, 'value': timeframe} for timeframe in available_timeframes],
        value='1min',
        clearable=False,
        style={'width': '200px'}
    ),

    # Dropdown to select indicators
    dcc.Dropdown(
        id='indicator-selector',
        options=[{'label': indicator, 'value': indicator} for indicator in indicators],
        multi=True,
        placeholder='Select Indicators',
        style={'width': '200px'}
    ),

    # Graph element for candlestick chart
    dcc.Graph(
        id='candlestick-chart',
        config={'displayModeBar': True},
        style={'height': '800px'}
    ),

    # Next button
    html.Button('Next', id='next-button', n_clicks=0)
])

# Single callback for both dropdowns and next button
@app.callback(
    Output('candlestick-chart', 'figure'),
    [Input('timeframe-selector', 'value'),
     Input('indicator-selector', 'value'),
     Input('next-button', 'n_clicks')]
)
def update_chart(selected_timeframe, selected_indicators, n_clicks):
    # Initial number of candles to display
    initial_size = 1000

    # Track how many points to show, starting with initial_size, then adding n_clicks
    total_points = initial_size + n_clicks

    # Get the slice of data based on clicks
    new_data = convert_timeframe(data, selected_timeframe).iloc[:total_points]

    # Initialize figure
    fig = go.Figure(data=[go.Candlestick(
        x=new_data.index,
        open=new_data['Open'],
        high=new_data['High'],
        low=new_data['Low'],
        close=new_data['Close']
    )])

    # Update indicators if present
    if selected_indicators:
        for indicator in selected_indicators:
            if indicator in new_data.columns:
                fig.add_trace(go.Scatter(x=new_data.index, y=new_data[indicator], mode='lines', name=indicator))

    fig.update_layout(title=f'Candlestick Chart ({selected_timeframe}) - {total_points} Candles',
                      xaxis_title='Date', yaxis_title='Price')

    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
