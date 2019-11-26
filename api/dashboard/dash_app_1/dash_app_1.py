from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import pandas_datareader as pdr
from dash import Dash
from dash.dependencies import Input, Output
from pandas import DataFrame

from api.dashboard.dash_function import apply_layout
from api.helpers.check_token_type_decorator import jwt_required_extended

url_base = '/dash/info/'

layout = html.Div([
    html.H1('Occupancy Viewer'),
    dcc.Dropdown(id='my-dropdown',
                 options=[{
                     'label': 'temperature',
                     'value': 'temp'
                 }, {
                     'label': 'minimum temperature',
                     'value': 'temp_min'
                 }, {
                     'label': 'maximum temperature',
                     'value': 'temp_max'
                 }],
                 value='temp'),
    dcc.Graph(id='my-graph')
], style={'width': '500'})

def add_dash(server):
    app = Dash(server=server, url_base_pathname=url_base)
    apply_layout(app, layout)

    def retrieve_data():
        from api.models import DataSourceData, Weather, Forecast
        from playhouse.shortcuts import model_to_dict

        from api.helpers.data_frame_helper import (flatten_json_data_in_column,
                                                   filter_column_json_data)

        data_source_data_df = DataFrame(
            list(DataSourceData.select().where(
                DataSourceData.data_source_id == 2).dicts()))

        hourly_weather_query = Weather.select().where(
            Weather.weather_forecast_type == Forecast.HOURLY)
        hourly_filter = "{dt: dt,  weather: {main: weather[*].main,"\
            "description: weather[*].description}, main: main, wind: wind"\
            ", rain: rain, clouds: clouds}"
        hourly_weather_array = []
        for weather in hourly_weather_query:
            hourly_weather_array.append(model_to_dict(weather, recurse=False))

        hourly_weater_df = DataFrame(hourly_weather_array)
        hourly_weater_df = filter_column_json_data(hourly_weater_df, 'data',
                                                   hourly_filter)
        hourly_weater_df = flatten_json_data_in_column(hourly_weater_df,
                                                       'data')
        return {
            "data_source_data_df": data_source_data_df,
            "hourly_weather_data_df": hourly_weater_df
        }

    @app.callback(Output('my-graph', 'figure'),
                  [Input('my-dropdown', 'value')])
    @jwt_required_extended
    def update_graph(selected_dropdown_value):
        # df = pdr.get_data_yahoo(selected_dropdown_value,
        #                         start=dt(2017, 1, 1),
        #                         end=dt.now())
        df = retrieve_data()
        print(df)
        # return {
        #     'data': [{
        #         'x': df.index,
        #         'y': df.Close
        #     }],
        #     'layout': {
        #         'margin': {
        #             'l': 40,
        #             'r': 0,
        #             't': 20,
        #             'b': 30
        #         }
        #     }
        # }
        return {
            'data': [{
                'x': df['data_source_data_df'][['created_date']],
                'y': df['data_source_data_df'][['no_of_clients']],
                'name': 'Temperature in Celcius'
            }, {
                'x':
                df['hourly_weather_data_df'][['created_date']],
                'y':
                df['hourly_weather_data_df'][[
                    f'data_main.{selected_dropdown_value}'
                ]],
                'name':
                'Number of clients'
            }]
        }

    return app.server
