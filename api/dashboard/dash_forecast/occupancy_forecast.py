from datetime import datetime, timedelta

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Input, Output
from pandas import (DataFrame, read_pickle, read_json,
                    to_datetime, DatetimeIndex)

from api.dashboard.dash_function import apply_layout
from api.helpers.data_frame_helper import cached_dataframe_outdated
from api.settings import GET_PATH

url_base = '/dash/app2/'
_data_initialized = False

# minus_one_month = timedelta(days=28, hours=6)


def _get_start_and_end_of_week():
    import datetime as dt
    # today = dt.datetime.today() - minus_one_month
    today = dt.datetime.today()
    start_of_week = today - dt.timedelta(days=today.weekday())
    end_of_week = start_of_week + dt.timedelta(days=6)
    return start_of_week, end_of_week


def _get_current_hour_range(return_with_date: bool = False):
    import datetime as dt
    # start_date = dt.datetime.today() - minus_one_month
    start_date = dt.datetime.today()
    start = start_date.replace(minute=0, second=0)
    end = dt.datetime.strftime(
        start + dt.timedelta(minutes=59), '%Y-%m-%d %H:%M:00')
    start = dt.datetime.strftime(start, '%Y-%m-%d %H:%M:00')
    if not return_with_date:
        end = end.split()[1]
        start = start.split()[1]
    return start, end


def _retrieve_forecast_data():
    from api.services import ForecastService as _ForecastService
    start_date, end_date = _get_start_and_end_of_week()
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    data_frame = read_json(_ForecastService.get_crowd_forecast(
        _ForecastService, start_date, end_date, True))
    # Adds timezone
    data_frame['created_date'] = to_datetime(
        data_frame['created_date'], unit='ms').astype(
            'datetime64[ns, Europe/Amsterdam]')
    return data_frame


def _retrieve_current_clients(data_source_id: int = 2):
    from api.models import DataSourceData
    start_week, end_week = _get_start_and_end_of_week()
    start_week = start_week.strftime('%Y-%m-%d')
    end_week = end_week.strftime('%Y-%m-%d')
    data_source_data_df = DataFrame(
        list(DataSourceData.select().where(
            DataSourceData.data_source_id == data_source_id,
            DataSourceData.created_date >= start_week,
            DataSourceData.created_date <= end_week).dicts()))
    if not data_source_data_df.empty:
        data_source_data_df['created_date'] = data_source_data_df[
            'created_date'].map(lambda x: x.replace(second=0))
        # substract the number of always connected clients
        data_source_data_df['no_of_clients'] = data_source_data_df[
            'no_of_clients'] - 8
        data_source_data_df.loc[
            data_source_data_df['no_of_clients'] < 0, 'no_of_clients'] = 0
    return data_source_data_df


day_of_week_names = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]

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
                    html.Label('Show day of the week'),
                    dcc.Dropdown(
                        id='day-of-week-dropdown',
                        options=[{
                            'label': 'Monday',
                            'value': 0
                        }, {
                            'label': 'Tuesday',
                            'value': 1
                        }, {
                            'label': 'Wednesday',
                            'value': 2
                        }, {
                            'label': 'Thursday',
                            'value': 3
                        }, {
                            'label': 'Friday',
                            'value': 4
                        }, {
                            'label': 'Saturday',
                            'value': 5
                        }, {
                            'label': 'Sunday',
                            'value': 6
                        }],
                        value=datetime.today().weekday(),
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


def add_dash(server):
    dash_app = Dash(__name__, server=server, url_base_pathname=url_base,
                    assets_folder=GET_PATH() + '/static')
    apply_layout(dash_app, layout)

    @dash_app.callback(Output('occupancy-forecast', 'figure'), [
        Input('day-of-week-dropdown', 'value')
    ])
    def update_graph(
            selected_dropdown_value):
        global _data_initialized
        crowd_forecast_df = DataFrame()
        current_clients_df = DataFrame()

        # Try to read data from cache
        try:
            crowd_forecast_df = read_pickle('cached_crowd_forecast_df.pkl')
        except BaseException:
            pass

            # Initializes the data once on application startup
        if not _data_initialized:
            if crowd_forecast_df.empty or current_clients_df.empty:
                crowd_forecast_df = _retrieve_forecast_data()
                crowd_forecast_df.to_pickle('cached_crowd_forecast_df.pkl')
                current_clients_df = _retrieve_current_clients()
                current_clients_df.to_pickle('cached_clients_df.pkl')
            else:
                # Check if cache is outdated
                if cached_dataframe_outdated('cached_crowd_forecast_df.pkl',
                                             'hours', 1):
                    crowd_forecast_df = _retrieve_forecast_data()
                    crowd_forecast_df.to_pickle(
                        'cached_crowd_forecast_df.pkl')
                    current_clients_df = _retrieve_current_clients()
                    current_clients_df.to_pickle('cached_clients_df.pkl')
                crowd_forecast_df = read_pickle(
                    'cached_crowd_forecast_df.pkl')
                current_clients_df = read_pickle(
                    'cached_clients_df.pkl'
                )
            _data_initialized = True

        crowd_forecast_df.loc[
            crowd_forecast_df[
                'predicted_no_of_clients'] < 0.7,
            'predicted_no_of_clients'] = 0

        current_clients_df = _retrieve_current_clients()
        if selected_dropdown_value is not None:
            filtered_forecast_df = crowd_forecast_df.loc[
                crowd_forecast_df['day_of_week'] == selected_dropdown_value]

        figure = go.Figure()

        figure.add_trace(
            go.Bar(x=filtered_forecast_df['created_date'],
                   y=filtered_forecast_df['predicted_no_of_clients'],
                   hoverinfo='skip',
                   base=0,
                   marker=go.bar.Marker(
                       color='rgb(63, 81, 181)'
            )))

        # Converts string to datetime64 type
        current_clients_df[
            'created_date'] = current_clients_df[
            'created_date'].astype('datetime64[ns]')
        current_clients_df['day_of_week'] = current_clients_df[
            'created_date'].dt.dayofweek
        # Extract YYYY-mm-dd format from converted datetime64 type
        # This new field is used for querying
        current_clients_df['date'] = to_datetime(
            current_clients_df['created_date'], format='%Y-%m-%d')
        current_clients_df = current_clients_df[(
            current_clients_df['day_of_week'] == selected_dropdown_value
        )]

        # Query to retrieve today's date
        # today_date = datetime.today() - minus_one_month
        today_date = datetime.today()
        start_date = today_date.replace(minute=0, second=0)
        end_date = datetime.strftime(
            start_date + timedelta(minutes=59), '%Y-%m-%d')
        current_clients_df_filtered = current_clients_df[(
            current_clients_df['date'] >= start_date
        )]
        current_clients_df_filtered = current_clients_df_filtered[(
            current_clients_df_filtered['date'] <= end_date
        )]

        current_clients_df['index_created_date'] = DatetimeIndex(
            current_clients_df['created_date'])
        current_clients_df = current_clients_df.set_index('index_created_date')
        # Get start hour and end hour using current time
        start_time, end_time = _get_current_hour_range()
        current_clients_df_filtered = current_clients_df.between_time(
            start_time, end_time)

        if not current_clients_df_filtered.empty and (
                selected_dropdown_value == today_date.weekday()):
            figure.add_trace(
                go.Bar(x=[current_clients_df_filtered.iloc[0]['created_date']],
                       y=[current_clients_df_filtered['no_of_clients'].mean()],
                       hoverinfo='skip',
                       base=0,
                       opacity=0.5,
                       marker=go.bar.Marker(
                    color='rgb(253, 80, 3)'
                )))

        figure.update_yaxes(
            range=[0, current_clients_df.no_of_clients.max() + 5],
            dtick=5,
            autorange=False,
            showticklabels=False
        )

        figure.update_layout(
            title=f"Predicted crowdedness for "
            f"{day_of_week_names[selected_dropdown_value]}",
            margin={'l': 20, 'r': 20, 't': 50, 'b': 0},
        )

        return figure

    return dash_app.server
