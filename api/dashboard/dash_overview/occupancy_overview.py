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

url_base = '/dash/app1/'
_data_initialized = False

layout = html.Div([
    html.Div([
        html.Div([
            html.H1('Occupancy Overview'),
        ], className="col")
    ], className="row"),
    html.Div([
        html.Details([
            html.Summary('Filters'),
            html.Div([
                html.Div([
                    html.Label('Show line of'),
                    dcc.Dropdown(
                        id='my-dropdown',
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
                        multi=True,
                        className=""),
                ], className="form-group"),

                html.Div([
                    html.Label('View date range'),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        min_date_allowed=dt(2019, 11, 1),
                        start_date=('2019-11-08'),
                        # initial_visible_month=dt(2019, 11, 1),
                        className=""
                    ),
                ], className="form-group"),

                html.Div([
                    html.Label('Retrieve latest data'),
                    html.Button('Refresh data', id='refresh-data-button',
                                type='button', className='button-dash'),
                ], className="form-group"),
            ], className="form-group col-xs-10 col-sm-8 col-md-12"),
        ], className="form-horizontal col"),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='occupancy-graph')
        ], className="col"),
    ], className="row")
])

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
    # floors the seconds to 0, move it to the server function so that the user can
    # interact with it.
    data_source_data_df['created_date'] = data_source_data_df['created_date'].map(
        lambda x: x.replace(second=0))
    hourly_weather_query = Weather.select().where(
        Weather.weather_forecast_type == Forecast.HOURLY)
    hourly_filter = "{dt: dt,  weather: {main: weather[0].main,"\
        "description: weather[0].description}, main: main, wind: wind"\
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

# flake8: noqa: C901

def add_dash(server):
    dash_app = Dash(__name__, server=server, url_base_pathname=url_base,
                    assets_folder=GET_PATH() + '/static')
    apply_layout(dash_app, layout)

    @dash_app.callback(Output('occupancy-graph', 'figure'), [
        Input('my-dropdown', 'value'),
        Input('refresh-data-button', 'n_clicks'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        # Input('time-offset-input', 'time_input'),
        # Input('date-offset-dropdown', 'date_offset')
    ])
    @jwt_required_extended
    def update_graph(
            selected_dropdown_value,
            n_clicks,
            start_date,
            end_date,
            # time_input,
            # date_offset
            ):
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
