from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import pandas_datareader as pdr
from dash import Dash
from dash.dependencies import Input, Output

from api.dashboard.dash_function import apply_layout
from api.helpers.check_token_type_decorator import jwt_required_extended

url_base = '/dash/stock/'

layout = html.Div([
    html.H1('Stock Tickers'),
    dcc.Dropdown(id='my-dropdown',
                 options=[{
                     'label': 'Coke',
                     'value': 'COKE'
                 }, {
                     'label': 'Tesla',
                     'value': 'TSLA'
                 }, {
                     'label': 'Apple',
                     'value': 'AAPL'
                 }],
                 value='COKE'),
    dcc.Graph(id='my-graph')
], style={'width': '500'})


def add_dash(server):
    app = Dash(server=server, url_base_pathname=url_base)
    apply_layout(app, layout)

    @app.callback(Output('my-graph', 'figure'),
                  [Input('my-dropdown', 'value')])
    @jwt_required_extended
    def update_graph(selected_dropdown_value):
        df = pdr.get_data_yahoo(selected_dropdown_value,
                                start=dt(2017, 1, 1),
                                end=dt.now())
        return {
            'data': [{
                'x': df.index,
                'y': df.Close
            }],
            'layout': {
                'margin': {
                    'l': 40,
                    'r': 0,
                    't': 20,
                    'b': 30
                }
            }
        }

    return app.server
