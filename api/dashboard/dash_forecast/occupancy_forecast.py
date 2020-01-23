from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Input, Output
from pandas import DataFrame, read_pickle

from api.dashboard.dash_function import apply_layout
from api.helpers.check_token_type_decorator import jwt_required_extended
from api.helpers.data_frame_helper import cached_dataframe_outdated
from api.settings import GET_PATH

url_base = '/dash/app2/'

# flake8: noqa: C901

def add_dash(server):
    dash_app = Dash(__name__, server=server, url_base_pathname=url_base,
                    assets_folder=GET_PATH() + '/static')
    apply_layout(dash_app, alternative_layout)

    @dash_app.callback(Output('occupancy-graph', 'figure'), [
        Input('my-dropdown', 'value'),
        Input('refresh-data-button', 'n_clicks'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('time-offset-input', 'value'),
        Input('date-offset-dropdown', 'value')
    ])
    @jwt_required_extended
    def update_graph(
            selected_dropdown_value,
            n_clicks,
            start_date,
            end_date,
            time_input,
            date_offset):
        global _data_initialized
        data_source_data_df = DataFrame()
        hourly_weather_data_df = DataFrame()
        # Try to read data from cache
        try:
            data_source_data_df = read_pickle('cached_data_source_data_df.pkl')
            hourly_weather_data_df = read_pickle(
                'cached_hourly_weather_data_df.pkl')
        except BaseException:
            pass

        # Initializes the data once on application startup
        if not _data_initialized:
            if data_source_data_df.empty or hourly_weather_data_df.empty:
                dictionary_df = _retrieve_data()
                data_source_data_df = dictionary_df['data_source_data_df']
                data_source_data_df.to_pickle('cached_data_source_data_df.pkl')
                hourly_weather_data_df = dictionary_df[
                    'hourly_weather_data_df']
                hourly_weather_data_df.to_pickle(
                    'cached_hourly_weather_data_df.pkl')
            else:
                # Check if cache is outdated
                if cached_dataframe_outdated('cached_data_source_data_df.pkl',
                                             'hours', 1):
                    dictionary_df = _retrieve_data()
                    data_source_data_df = dictionary_df['data_source_data_df']
                    data_source_data_df.to_pickle(
                        'cached_data_source_data_df.pkl')
                    hourly_weather_data_df = dictionary_df[
                        'hourly_weather_data_df']
                    hourly_weather_data_df.to_pickle(
                        'cached_hourly_weather_data_df.pkl')
                data_source_data_df = read_pickle(
                    'cached_data_source_data_df.pkl')
                hourly_weather_data_df = read_pickle(
                    'cached_hourly_weather_data_df.pkl')
            _data_initialized = True

        # Prevents click event from firing on application startup
        if n_clicks is not None:
            dictionary_df = _retrieve_data()
            data_source_data_df = dictionary_df['data_source_data_df']
            data_source_data_df.to_pickle('cached_data_source_data_df.pkl')
            hourly_weather_data_df = dictionary_df['hourly_weather_data_df']
            hourly_weather_data_df.to_pickle(
                'cached_hourly_weather_data_df.pkl')

        if start_date is not None:
            start_date = dt.strptime(start_date.split(' ')[0], '%Y-%m-%d')
            data_source_data_df = data_source_data_df[(
                data_source_data_df['created_date'] >= start_date)]
            hourly_weather_data_df = hourly_weather_data_df[(
                hourly_weather_data_df['created_date'] >= start_date
            )]
        if end_date is not None:
            end_date = dt.strptime(end_date.split(' ')[0], '%Y-%m-%d')
            data_source_data_df = data_source_data_df[(
                data_source_data_df['created_date'] <= end_date)]
            hourly_weather_data_df = hourly_weather_data_df[(
                hourly_weather_data_df['created_date'] <= end_date
            )]

        figure = go.Figure()

        figure.add_trace(
            go.Bar(x=data_source_data_df['created_date'],
                   y=data_source_data_df['no_of_clients'],
                   name='Number of clients',
                   hovertemplate='<b>Connected clients</b>: %{y}' +
                   '<br>date: %{x} </br>',
                   marker=go.bar.Marker(
                       color='rgb(63, 81, 181)'
            )))

        for dropdown_value in selected_dropdown_value:
            if dropdown_value in temperature_label_dict:
                figure.add_trace(
                    go.Scatter(
                        x=hourly_weather_data_df['created_date'],
                        y=hourly_weather_data_df[
                            f'data_main.{dropdown_value}'],
                        hovertemplate='<br><b>' +
                        f'{temperature_label_dict.get(dropdown_value)}</b>:'
                        ' %{y}℃</br>' +
                        'date: %{x}',
                        name=f'{temperature_label_dict.get(dropdown_value)}'))

        figure.update_xaxes(hoverformat='%c')
        figure.update_layout(
            showlegend=True,
            legend_orientation="h",
            legend=dict(x=0, y=1.1),
            margin={'l': 50, 'r': 50, 't': 0, 'b': 0}
        )
        return figure

    return dash_app.server
