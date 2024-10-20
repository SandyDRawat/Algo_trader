import dash 
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from Ingest.data_ingest import data_in_csv  # Assuming the function is inside this module
from preprocessing.cleaning import data_cleaning  # Assuming the cleaning logic is in this module
from preprocessing.timeframe import convert_timeframe
from Charts.candle_chart import interactive_candle_chart  # Assuming this function is defined as provided
from indicators.indicator import sma, ema, rsi

# Step 2: Initialize Dash App
app = dash.Dash(__name__)

# Filepath to the dataset
file_path = 'data/NIFTY50-Minute_data.csv'

# Load and prepare the data
data = data_cleaning(data_in_csv(file_path)).head(5000)  # Increased data size
data = sma(data)
data = ema(data)
data = rsi(data)

# Collect available timeframes and indicators
available_timeframes = ['1min', '5min', '15min', '30min', '1h']
indicators = [col for col in data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Date']]

# Step 3: Define Layout of the Dash App
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
            'editable': True  # Enables the ability to edit shapes (rectangles, lines)
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
    dcc.Store(id='shapes-store', data=[]),  # Store for shapes
    dcc.Store(id='zoom-store', data={}),    # Store for zoom/pan
    dcc.Store(id='positions-store', data={'position': None, 'entry_price': None}),  # Store for positions
    dcc.Store(id='pnl-store', data=0)  # Store for PnL
])

# Step 4: Create a single callback for dropdowns and button
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
    # Initial number of candles to display
    initial_size = 1000

    # Track how many points to show, starting with initial_size, then adding n_clicks
    total_points = initial_size + n_clicks * 1  # Adjust the increment as needed

    # Get the slice of data based on clicks
    new_data = convert_timeframe(data, selected_timeframe).iloc[:total_points]

    # Use the interactive candlestick chart function
    fig = interactive_candle_chart(new_data, show_fig=False)

    # Update candlestick traces with the new data
    fig.data[0].x = new_data.index
    fig.data[0].open = new_data['Open']
    fig.data[0].high = new_data['High']
    fig.data[0].low = new_data['Low']
    fig.data[0].close = new_data['Close']

    # Add selected indicators to the chart
    if selected_indicators:
        for indicator in selected_indicators:
            if indicator in new_data.columns:
                fig.add_trace(go.Scatter(x=new_data.index, y=new_data[indicator], mode='lines', name=indicator))

    # Preserve zoom from relayoutData or stored zoom
    if relayout_data:
        # Store the zoom/pan settings
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
        if 'yaxis.range[0]' in stored_zoom and 'yaxis.range[1]' in stored_zoom:
            fig.update_yaxes(range=[stored_zoom['yaxis.range[0]'], stored_zoom['yaxis.range[1]']])

    # Reapply shapes from stored_shapes
    if stored_shapes:
        fig.update_layout(shapes=stored_shapes)

    # Preserve the title and axis labels
    fig.update_layout(
        title=f'Candlestick Chart ({selected_timeframe}) - {total_points} Candles',
        xaxis_title='Date', yaxis_title='Price'
    )

    return fig

# Step 5: Callback to store shapes and zoom/pan data
@app.callback(
    [Output('shapes-store', 'data'),
     Output('zoom-store', 'data')],
    [Input('candlestick-chart', 'relayoutData')],
    [State('shapes-store', 'data'),
     State('zoom-store', 'data')]
)
def store_shapes_and_zoom(relayout_data, current_shapes, current_zoom):
    if relayout_data:
        # Preserve shapes if they're drawn
        if 'shapes' in relayout_data:
            current_shapes = relayout_data['shapes']

        # Preserve zoom/pan data if available
        current_zoom = {
            'xaxis.range[0]': relayout_data.get('xaxis.range[0]', current_zoom.get('xaxis.range[0]', None)),
            'xaxis.range[1]': relayout_data.get('xaxis.range[1]', current_zoom.get('xaxis.range[1]', None)),
            'yaxis.range[0]': relayout_data.get('yaxis.range[0]', current_zoom.get('yaxis.range[0]', None)),
            'yaxis.range[1]': relayout_data.get('yaxis.range[1]', current_zoom.get('yaxis.range[1]', None))
        }

    return current_shapes, current_zoom

# Step 6: Execute trades and update PnL
@app.callback(
    [Output('positions-store', 'data'),
     Output('pnl-store', 'data'),
     Output('position-display', 'children'),
     Output('pnl-display', 'children')],
    [Input('buy-button', 'n_clicks'),
     Input('sell-button', 'n_clicks'),
     Input('next-button', 'n_clicks')],
    [State('positions-store', 'data'),
     State('pnl-store', 'data'),
     State('candlestick-chart', 'figure')]
)
def execute_trade(buy_clicks, sell_clicks, next_clicks, position_data, pnl, fig):
    ctx = dash.callback_context

    # Ensure fig and data are valid before accessing
    last_close = None
    if fig and 'data' in fig and fig['data']:
        last_close = fig['data'][0]['close'][-1]

    # Update PnL after pressing "Next"
    if next_clicks > 0 and last_close is not None:
        if position_data['position'] == 'buy':
            pnl = last_close - position_data['entry_price']  # Current PnL for long position
        elif position_data['position'] == 'sell':
            pnl = position_data['entry_price'] - last_close  # Current PnL for short position

    if ctx.triggered:
        if ctx.triggered[0]['prop_id'] == 'buy-button.n_clicks':
            if position_data['position'] == 'sell':  # Closing short position
                position_data['position'] = None  # Close position
                position_data['entry_price'] = None
            elif position_data['position'] == None and last_close is not None:  # Opening long position
                position_data['position'] = 'buy'
                position_data['entry_price'] = last_close

        elif ctx.triggered[0]['prop_id'] == 'sell-button.n_clicks':
            if position_data['position'] == 'buy':  # Closing long position
                position_data['position'] = None  # Close position
                position_data['entry_price'] = None
            elif position_data['position'] == None and last_close is not None:  # Opening short position
                position_data['position'] = 'sell'
                position_data['entry_price'] = last_close

    # Display current position and PnL
    position_display = f"Current Position: {position_data['position'] if position_data['position'] else 'None'}"
    pnl_display = f"Current PnL: {pnl:.2f}"

    return position_data, pnl, position_display, pnl_display

# Step 7: Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
