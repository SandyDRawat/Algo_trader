import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from preprocessing.data_ingest import data_in_csv
from preprocessing.cleaning import data_cleaning
from preprocessing.timeframe import convert_timeframe
from Charts.candle_chart import interactive_candle_chart
from preprocessing.indicator import sma, ema, rsi, macd, bollinger_bands, atr, garman_klass
from Practice.random import randomdate_data

# Initialize Dash App
app = dash.Dash(__name__)

# Filepath to the dataset
file_path = 'data/NIFTY50-Minute_data.csv'
data = data_cleaning(data_in_csv(file_path))

# Adding indicators to the data
data = sma(data)
data = ema(data)
data = rsi(data)
data = bollinger_bands(data)
data = macd(data)
data = atr(data)    
data = garman_klass(data)
data = randomdate_data(data)
print(data.tail(5))

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

    # Graph element for candlestick chart with increased height
    dcc.Graph(
        id='candlestick-chart',
        config={
            'displayModeBar': True,
            'scrollZoom': True,
            'modeBarButtonsToAdd': ['drawline', 'drawrect', 'drawcircle', 'eraseshape'],
            'editable': True
        },
        style={'height': '800px'}
    ),

    # Next button
    html.Button('Next', id='next-button', n_clicks=0),

    # Buy and Sell buttons
    html.Div([
        html.Button('Buy', id='buy-button', n_clicks=0),
        html.Button('Sell', id='sell-button', n_clicks=0)
    ]),

    # Display for current position and PnL
    html.Div(id='position-display'),
    html.Div(id='pnl-display'),

    # Hidden div to store drawings and relayout data
    dcc.Store(id='shapes-store', data=[]),
    dcc.Store(id='zoom-store', data={}),
    dcc.Store(id='positions-store', data={'position': None, 'entry_price': None}),
    dcc.Store(id='pnl-store', data=0)
])

# Update chart with selected indicators in subplots
@app.callback(
    Output('candlestick-chart', 'figure'),
    [Input('timeframe-selector', 'value'),
     Input('indicator-selector', 'value'),
     Input('next-button', 'n_clicks')],
    [State('candlestick-chart', 'relayoutData'),
     State('shapes-store', 'data'),
     State('zoom-store', 'data')]
)
def update_chart(selected_timeframe, selected_indicators, n_clicks, relayout_data, stored_shapes, stored_zoom):
    initial_size = 1080 + 45
    total_points = initial_size + n_clicks * 1

    new_data = convert_timeframe(data, selected_timeframe).iloc[:total_points]
    print(new_data.tail(5))

    # Create subplots, setting the number of rows based on indicators
    num_subplots = 1 + len(selected_indicators)
    fig = make_subplots(rows=num_subplots, cols=1, shared_xaxes=True,
                        row_heights=[0.5] + [0.2] * (num_subplots - 1),
                        vertical_spacing=0.05)

    # Add the candlestick chart to the first row
    fig.add_trace(go.Candlestick(
        x=new_data.index,
        open=new_data['Open'],
        high=new_data['High'],
        low=new_data['Low'],
        close=new_data['Close'],
        name='Candlestick'
    ), row=1, col=1)

    # Loop through selected indicators and add them to their respective subplots
    for idx, indicator in enumerate(selected_indicators):
        if indicator in new_data.columns:
            row_num = idx + 2  # Start from the second row
            
            if indicator == 'RSI':
                fig.add_trace(go.Scatter(x=new_data.index, y=new_data[indicator], mode='lines', name=indicator), row=row_num, col=1)
                fig.update_yaxes(title_text=indicator, row=row_num, col=1, range=[0, 100])  # RSI range 0-100
            else:
                fig.add_trace(go.Scatter(x=new_data.index, y=new_data[indicator], mode='lines', name=indicator), row=row_num, col=1)
                fig.update_yaxes(title_text=indicator, row=row_num, col=1)

    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["15:40", "09:05"])
        ]
    )

    # Preserve zoom from relayoutData or stored zoom
    if relayout_data:
        stored_zoom = {
            'xaxis.range[0]': relayout_data.get('xaxis.range[0]', None),
            'xaxis.range[1]': relayout_data.get('xaxis.range[1]', None),
            'yaxis.range[0]': relayout_data.get('yaxis.range[0]', None),
            'yaxis.range[1]': relayout_data.get('yaxis.range[1]', None)
        }

    # Apply stored zoom/pan settings
    if stored_zoom:
        if 'xaxis.range[0]' in stored_zoom and 'xaxis.range[1]' in stored_zoom:
            fig.update_xaxes(range=[stored_zoom['xaxis.range[0]'], stored_zoom['xaxis.range[1]']])

    if stored_shapes:
        fig.update_layout(shapes=stored_shapes)

    fig.update_layout(
        title=f'Candlestick Chart ({selected_timeframe}) - {total_points} Candles',
        xaxis_title='Date', yaxis_title='Price'
    )

    fig.update_xaxes(rangebreaks=[dict(bounds=[16, 9], pattern="hour"),
                              dict(bounds=['sat', 'mon'])
                              ])

    return fig

# Rest of your callbacks remain unchanged...

if __name__ == '__main__':
    app.run_server(debug=True)
