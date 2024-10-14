import plotly.graph_objects as go

# Sample data
x = [1, 2, 3, 4, 5]
y_initial = [10, 11, 12, 13, 14]
y_updated = [15, 14, 13, 12, 11]

# Create the initial plot
fig = go.Figure(data=[go.Scatter(x=x, y=y_initial, mode='lines+markers', name="Initial Data")])

# Layout customization
fig.update_layout(
    title="Simple Line Plot with Update Button",
    xaxis_title="X",
    yaxis_title="Y"
)

# Add button to update the data
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="left",
            buttons=[
                dict(
                    label="Update Data",
                    method="restyle",  # 'restyle' is used to update the data
                    args=[{'y': [y_updated]}],  # Update 'y' with new data
                    execute=True  # Ensures the button action is immediate
                )
            ],
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.17,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )
    ]
)

# Show the plot
fig.show()
