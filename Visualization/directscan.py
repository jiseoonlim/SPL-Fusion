import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import time

# 초기 데이터 설정
app = dash.Dash(__name__)
df = pd.DataFrame(columns=['x', 'y', 'z'])

app.layout = html.Div([
    dcc.Graph(id='live-3d-plot'),
    dcc.Interval(id='interval-update', interval=1000, n_intervals=0)  # 1초마다 업데이트
])

@app.callback(
    Output('live-3d-plot', 'figure'),
    [Input('interval-update', 'n_intervals')]
)
def update_plot(n):
    global df
    # 새로운 데이터 수집 (예제 데이터로 대체)
    new_data = pd.DataFrame([[n * 0.5, n * 0.2, n]], columns=['x', 'y', 'z'])
    df = pd.concat([df, new_data], ignore_index=True)
    
    scatter = go.Scatter3d(
        x=df['x'], y=df['y'], z=df['z'],
        mode='markers',
        marker=dict(size=3, color=df['z'], colorscale='Viridis', opacity=0.8)
    )
    
    fig = go.Figure(data=[scatter])
    fig.update_layout(scene=dict(
        xaxis=dict(range=[-100, 100]),
        yaxis=dict(range=[-100, 100]),
        zaxis=dict(range=[0, 150])
    ))
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
