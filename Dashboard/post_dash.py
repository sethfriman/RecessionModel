# This file will be where the dashboard is deployed from

import warnings
warnings.filterwarnings("ignore")
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import sys

sys.path.append("../")
from CodeBase.Data.data_viz import Visualizer

app = dash.Dash()
vis = Visualizer()

fig = vis.scatPlot2('yield_diff', 'years_until_recession')

app.layout = html.Div([dcc.Graph(id='yur-vs-yield_diff', figure=fig)])

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')

