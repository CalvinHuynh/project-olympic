import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
from dash.dependencies import Input, Output

from .dash_helper import apply_layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
url_base = '/dash/'
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Graph(id='example-graph',
              figure={
                  'data': [
                      {
                          'x': [1, 2, 3],
                          'y': [4, 1, 2],
                          'type': 'bar',
                          'name': 'SF'
                      },
                      {
                          'x': [1, 2, 3],
                          'y': [2, 4, 5],
                          'type': 'bar',
                          'name': u'Montréal'
                      },
                  ],
                  'layout': {
                      'title': 'Dash Data Visualization'
                  }
              })
])


def Add_Dash(server):
    app = Dash(server=server, url_base_pathname=url_base)
    apply_layout(app, layout)

    @app.callback(Output('target', 'children'), [Input('input_text', 'value')])
    def callback_fun(value):
        return 'your input is {}'.format(value)

    return app.server
