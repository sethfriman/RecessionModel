import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__)

layout = html.Div(children=[
    html.H1(children='This is our Data Description page'),

    html.Div(children='''
        Coming Soon
    '''),

])