import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Input, Output
from pandas import DataFrame, read_pickle

from api.dashboard.dash_function import apply_layout
from api.helpers.check_token_type_decorator import jwt_required_extended
from api.helpers.data_frame_helper import cached_dataframe_outdated

url_base = '/dash/info/'
_data_initialized = False

layout = html.Div([
    html.H1('Occupancy Viewer'),
    dcc.Dropdown(id='my-dropdown',
                 options=[{
                     'label': 'Current temperature',
                     'value': 'temp'
                 }, {
                     'label': 'Minimum temperature',
                     'value': 'temp_min'
                 }, {
                     'label': 'Maximum temperature',
                     'value': 'temp_max'
                 }],
                 value=['temp'],
                 multi=True),
    html.Button(
        'Refresh data',
        id='refresh-data-button',
    ),
    dcc.Graph(id='occupancy-graph')
], style={'width': '500'})

temperature_label_dict = {
    'temp': 'Current temperature',
    'temp_min': 'Minimum temperature',
    'temp_max': 'Maximum temperature'
}


def _retrieve_data(data_source_id: int = 2):
    from api.models import DataSourceData, Weather, Forecast
    from playhouse.shortcuts import model_to_dict

    from api.helpers.data_frame_helper import (flatten_json_data_in_column,
                                               filter_column_json_data)

    data_source_data_df = DataFrame(
        list(DataSourceData.select().where(
            DataSourceData.data_source_id == data_source_id).dicts()))

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
    hourly_weater_df = flatten_json_data_in_column(hourly_weater_df, 'data')
    return {
        "data_source_data_df": data_source_data_df,
        "hourly_weather_data_df": hourly_weater_df
    }


def add_dash(server):
    app = Dash(server=server, url_base_pathname=url_base)
    apply_layout(app, layout)

    @app.callback(Output('occupancy-graph', 'figure'), [
        Input('my-dropdown', 'value'),
        Input('refresh-data-button', 'n_clicks')
    ])
    @jwt_required_extended
    def update_graph(selected_dropdown_value, n_clicks):
        global _data_initialized
        data_source_data_df = DataFrame()
        hourly_weather_data_df = DataFrame()
        try:
            data_source_data_df = read_pickle('cached_data_source_data_df.pkl')
            hourly_weather_data_df = read_pickle(
                'cached_hourly_weather_data_df.pkl')
        except BaseException:
            pass

        if not _data_initialized:
            if data_source_data_df.empty or hourly_weather_data_df.empty:
                print('initializing dataframe')
                dictionary_df = _retrieve_data()
                data_source_data_df = dictionary_df['data_source_data_df']
                data_source_data_df.to_pickle('cached_data_source_data_df.pkl')
                hourly_weather_data_df = dictionary_df[
                    'hourly_weather_data_df']
                hourly_weather_data_df.to_pickle(
                    'cached_hourly_weather_data_df.pkl')
            else:
                if cached_dataframe_outdated('cached_data_source_data_df.pkl',
                                             'hours', 1):
                    print('cache outdated')
                    dictionary_df = _retrieve_data()
                    data_source_data_df = dictionary_df['data_source_data_df']
                    data_source_data_df.to_pickle(
                        'cached_data_source_data_df.pkl')
                    hourly_weather_data_df = dictionary_df[
                        'hourly_weather_data_df']
                    hourly_weather_data_df.to_pickle(
                        'cached_hourly_weather_data_df.pkl')
                print('reading from cache')
                data_source_data_df = read_pickle(
                    'cached_data_source_data_df.pkl')
                hourly_weather_data_df = read_pickle(
                    'cached_hourly_weather_data_df.pkl')
            _data_initialized = True

        if n_clicks is not None:
            print('click event fired')
            dictionary_df = _retrieve_data()
            data_source_data_df = dictionary_df['data_source_data_df']
            data_source_data_df.to_pickle('cached_data_source_data_df.pkl')
            hourly_weather_data_df = dictionary_df['hourly_weather_data_df']
            hourly_weather_data_df.to_pickle(
                'cached_hourly_weather_data_df.pkl')

        figure = go.Figure()

        for dropdown_value in selected_dropdown_value:
            if dropdown_value in temperature_label_dict:
                figure.add_trace(
                    go.Scatter(
                        x=hourly_weather_data_df['created_date'],
                        y=hourly_weather_data_df[
                            f'data_main.{dropdown_value}'],
                        name=f'{temperature_label_dict.get(dropdown_value)}'
                        f' in Celcius'))

        figure.add_trace(
            go.Bar(x=data_source_data_df['created_date'],
                   y=data_source_data_df['no_of_clients'],
                   name='Number of clients'))

        return figure

    return app.server
