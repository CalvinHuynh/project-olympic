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
_data_initialized = False


def _get_start_and_end_of_week():
  import datetime as dt
  today = dt.datetime.today()
  start_of_week = today - dt.timedelta(days=today.weekday())
  end_of_week = start_of_week + dt.timedelta(days=6)
  return start_of_week, end_of_week


def _retrieve_forecast_data():
    from api.services import ForecastService as _ForecastService
    start_date, end_date = _get_start_and_end_of_week()
    result = _ForecastService.get_crowd_forecast(
        _ForecastService, start_date, end_date)
    return result


def _retrieve_current_clients():
    pass


alternative_layout = html.Div([
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
                    html.Label('Show day of the week'),
                    dcc.Dropdown(
                        id='day-of-week-dropdown',
                        options=[{
                            'label': 'Monday',
                            'value': 'Monday'
                        }, {
                            'label': 'Tuesday',
                            'value': 'Tuesday'
                        }, {
                            'label': 'Wednesday',
                            'value': 'Wednesday'
                        }, {
                            'label': 'Thursday',
                            'value': 'Thursday'
                        }, {
                            'label': 'Friday',
                            'value': 'Friday'
                        }, {
                            'label': 'Saturday',
                            'value': 'Saturday'
                        }, {
                            'label': 'Sunday',
                            'value': 'Sunday'
                        }],
                        value=dt.today().strftime('%A'),
                        className=""),
                ], className="form-group"),
            ], className="form-group col-xs-10 col-sm-8 col-md-12"),
        ], className="form-horizontal col"),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='occupancy-forecast')
        ], className="col"),
    ], className="row")
])

# flake8: noqa: C901


def add_dash(server):
    dash_app = Dash(__name__, server=server, url_base_pathname=url_base,
                    assets_folder=GET_PATH() + '/static')
    apply_layout(dash_app, alternative_layout)

    @dash_app.callback(Output('occupancy-forecast', 'figure'), [
        Input('day-of-week-dropdown', 'value')
    ])
    @jwt_required_extended
    def update_graph(
            selected_dropdown_value):
        global _data_initialized
        crowd_forecast_df = DataFrame()
        current_clients_df = DataFrame()

        # Try to read data from cache
        try:
            crowd_forecast_df = read_pickle('cached_crowd_forecast_df.pkl')
            current_clients_df = read_pickle(
                'cached_current_clients_df.pkl')
        except BaseException:
            pass

                # Initializes the data once on application startup
        if not _data_initialized:
            if crowd_forecast_df.empty or current_clients_df.empty:
                crowd_forecast_df = _retrieve_forecast_data()
                crowd_forecast_df.to_pickle('cached_crowd_forecast_df.pkl')
                current_clients_df = _retrieve_current_clients()
                current_clients_df.to_pickle(
                    'cached_current_clients_df.pkl')
            else:
                # Check if cache is outdated
                if cached_dataframe_outdated('cached_crowd_forecast_df.pkl',
                                             'hours', 1):
                    crowd_forecast_df = _retrieve_forecast_data()
                    crowd_forecast_df.to_pickle(
                        'cached_crowd_forecast_df.pkl')
                    current_clients_df = _retrieve_current_clients
                    current_clients_df.to_pickle(
                        'cached_current_clients_df.pkl')
                crowd_forecast_df = read_pickle(
                    'cached_crowd_forecast_df.pkl')
                current_clients_df = read_pickle(
                    'cached_current_clients_df.pkl')
            _data_initialized = True

        pass

    return dash_app.server
