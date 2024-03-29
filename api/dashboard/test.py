import os as _os
from datetime import datetime as dt
from enum import Enum

import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dotenv import load_dotenv as _load_dotenv
from numpy import int as np_int
from pandas import DataFrame, Series, set_option, to_datetime, read_json
from pandas.io.json import json_normalize
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, MySQLDatabase, PrimaryKeyField)
from playhouse.mysql_ext import JSONField
from playhouse.shortcuts import model_to_dict
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV, ElasticNet, ElasticNetCV
from sklearn.metrics import mean_squared_error, r2_score, confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVR
from sklearn.preprocessing import RobustScaler, scale, StandardScaler, LabelEncoder
# from cytoolz.dicttoolz import merge

env_path = '/home/calvin/Projects/afstuderen/project-olympic/.env'
_load_dotenv(dotenv_path=env_path)

MYSQL_HOST = _os.getenv("MYSQL_HOST")
MYSQL_DATABASE = _os.getenv("MYSQL_DATABASE")
MYSQL_USER = _os.getenv("MYSQL_USER")
MYSQL_PASSWORD = _os.getenv("MYSQL_PASSWORD")

database = MySQLDatabase(MYSQL_DATABASE,
                         user=MYSQL_USER,
                         password=MYSQL_PASSWORD,
                         host=MYSQL_HOST if MYSQL_HOST else "127.0.0.1",
                         port=3306)


class Base(Model):
    class Meta:
        database = database
        legacy_table_names = False


class User(Base):
    id = PrimaryKeyField()
    username = CharField(unique=True, null=True)
    email = CharField(unique=True, null=False)
    join_date = DateTimeField()
    last_login_date = DateTimeField()


class DataSource(Base):
    id = PrimaryKeyField()
    source = CharField(unique=True, max_length=25)
    description = CharField()
    user = ForeignKeyField(User, related_name='added_by')


class DataSourceData(Base):
    id = PrimaryKeyField()
    data_source = ForeignKeyField(DataSource, related_name='send_by')
    no_of_clients = IntegerField()
    created_date = DateTimeField()


class Weather(Base):
    id = PrimaryKeyField()
    created_date = DateTimeField()
    data = JSONField()
    data_source = ForeignKeyField(DataSource, related_name='send_by')
    weather_forecast_type = CharField()


class CrowdForecast(Base):
    id = PrimaryKeyField(),
    created_date = DateTimeField()
    date_range_used = CharField(max_length=50)
    number_of_weeks_used = CharField(max_length=4)
    prediction_for_week_nr = CharField(max_length=2)
    prediction_start_date = CharField(max_length=20)
    prediction_end_date = CharField(max_length=20)
    prediction_data = JSONField()

    class Meta:
        indexes = (
            ((
                'date_range_used',
                'prediction_start_date',
                'prediction_end_date'
            ), True),
        )



class Forecast(Enum):
    """
    The 2 types of forecasts that are currently available for the free tier
    API of Openweathermap.
    """

    # Return the name instead of the value, as the name gives more
    # information

    def __str__(self):
        return str(self.name)

    HOURLY = 1
    FIVE_DAYS_THREE_HOUR = 2


def filter_json(expression: str, json_data: object):
    """Filters json data using JMESPath

    Arguments:
        expression {str} -- filter query
        json_data {object} -- json data to filter

    Returns:
        json -- filtered json data
    """
    from jmespath import search
    from json import dumps, loads
    try:
        return search(expression, loads(json_data))
    except Exception:
        data = dumps(json_data)
        return search(expression, loads(data))


def filter_column_json_data(data_frame: DataFrame, column_to_filter: str,
                            expression: str):
    """Filter all the json data of the data frame using JMESPath

    Arguments:
        data_frame {DataFrame} -- input dataframe
        column_to_filter {str} -- column to filter
        expression {str} -- filter query
    """
    for index in range(len(data_frame)):
        data_frame[column_to_filter].values[index] = filter_json(
            expression, data_frame[column_to_filter].values[index])
    return data_frame


def flatten_json_data_in_column(data_frame: DataFrame,
                                column_to_flatten: str,
                                range_to_flatten: int = None,
                                custom_prefix: str = None):
    """Flattens the json of a specific column of the given dataframe

    Arguments:
        data_frame {DataFrame} -- input dataframe
        column_to_flatten {str} -- column to flatten

    Keyword Arguments:
        range_to_flatten {int} -- able to flatten multiple columns that uses an
         index as identifier (default: None)
        custom_prefix {str} -- custom prefix for the flattened output
         (default: column)

    Returns:
        [type] -- [description]
    """
    prefix = None
    if custom_prefix:
        prefix = custom_prefix
    else:
        prefix = f'{column_to_flatten}_'

    if range_to_flatten:
        prefix = f'{column_to_flatten}_'
        for index in range(range_to_flatten):
            try:
                data_frame = data_frame.join(
                    json_normalize(data_frame[column_to_flatten + "_" +
                                              str(index)].tolist()).
                    add_prefix(prefix + str(index) + "_")).drop(
                        [column_to_flatten + "_" + str(index)], axis=1)
            except BaseException:
                pass
    else:
        data_frame = data_frame.join(
            json_normalize(data_frame[column_to_flatten].tolist()).add_prefix(
                prefix)).drop([column_to_flatten], axis=1)

    return data_frame


def unpack_json_array(data_frame: DataFrame, column_to_unpack: str):
    """Unpack json data of a specific column in the dataframe

    Arguments:
        data_frame {DataFrame} -- input dataframe
        column_to_unpack {str} -- column to unpack the json array from

    Returns:
        data_frame -- modified dataframe
    """
    return data_frame[column_to_unpack].apply(Series).merge(
        data_frame, left_index=True, right_index=True).drop([column_to_unpack],
                                                            axis=1)


def _rename_columns(col_name):
    if isinstance(col_name, int):
        return f'data_{col_name}'
    else:
        pass
    return col_name


def drop_columns_with_postfix(df: DataFrame, postfix_to_drop: str = '_y'):
    """Function to drop common columns after a merge

    Arguments:
        df {DataFrame} -- dataframe to drop columns from

    Keyword Arguments:
        postfix_to_drop {str} -- postfix of column to drop (default: {'_y'})

    Returns:
        {DataFrame} -- returns a dataframe with the matching columns dropped
    """
    all_columns_in_df = list(df)
    for col in all_columns_in_df:
        if col.endswith(postfix_to_drop):
            del df[col]
    return df


def convert_list_to_string(list_to_join: list):
    """Converts a given list to a comma separated string.

    Arguments:
        list_to_join {list} -- list to convert

    Returns:
        {str} -- returns a joined together string
    """
    return ", ".join(list_to_join)


def item_in_list(item: str, item_list: list):
    """Check if a given item is in a given list.
    If the given item occurs in a list, an 1 will be returned.
    Else a 0 will be returned.

    Arguments:
        item {str} -- item to check
        item_list {list} -- list of items

    Returns:
        {int} -- returns an 1 if item is in list, else 0.
    """
    if item in item_list:
        return True
    else:
        return False


def unix_to_datetime(
        data_frame: DataFrame,
        col_prefix: str = 'data_',
        col_postfix: str = '_dt',
        length: int = 40):
    """Converts unix timestamp column to datetime column

    Arguments:
        data_frame {DataFrame} -- dataframe containing unix timestamps

    Keyword Arguments:
        col_prefix {str} -- column name prefix (default: {'data_'})
        col_postfix {str} -- column name postfix (default: {'_dt'})
        length {int} -- flattened column range (default: {40})

    Returns:
        {DataFrame} -- returns dataframe containing the converted timestamps
    """
    for i in range(length):
        data_frame[f"{col_prefix}{i}{col_postfix}"] = to_datetime(
            data_frame[f"{col_prefix}{i}{col_postfix}"], unit='s')
    return data_frame


def strip_from_string(string_to_split: str, index: int = 2, strip_character: str = '_'):
    return strip_character.join(string_to_split.split(strip_character)[:index])


def _find_value_near_datetime(
        data_frame: DataFrame,
        column_name: str,
        value_to_find):
    idx = data_frame[column_name].sub(value_to_find).abs().idxmin()
    nearest_date = str(
        data_frame.loc[[idx]]['created_date'].values[0].astype(np_int) // 10**9
    )
    if (nearest_date > value_to_find.strftime('%s')):
        return data_frame.loc[[idx - 1]]
    else:
        return data_frame.loc[[idx]]


def fill_missing_values_using_forecast(
        missing_val_data_frame: DataFrame,
        forecast_data_frame: DataFrame,
        column_name: str):
    """
    Fill missing weather values using saved forecast data

    Arguments:
        missing_val_data_frame {DataFrame} -- data frame that contains missing
         weather values
        forecast_data_frame {DataFrame} -- data frame that contains the
         weather forecast, this data frame will be used to fill the missing
         weather values
        column_name {str} -- column name will be used to match the data frames
    Returns:
        {DataFrame} -- data frame that has been filled in using forecast data
    """
    for index, row in missing_val_data_frame.iterrows():
        forecast_row = _find_value_near_datetime(
            forecast_data_frame, column_name, row['created_date']
        )
        matching_col = forecast_row[forecast_row.columns[forecast_row.iloc[(
            0)] == row['created_date']]]
        if not matching_col.empty:
            col_prefix_to_match = strip_from_string(list(matching_col)[0])
            columns_to_fill = [
                '_main.temp', '_main.pressure', '_main.humidity',
                '_main.temp_min', '_main.temp_max', '_wind.speed',
                '_wind.deg', '_clouds.all', '_weather.main',
                '_weather.description', '_rain.3h', '_dt'
            ]
            for col_postfix in columns_to_fill:
                if col_postfix == '_dt':
                    missing_val_data_frame.loc[
                        index, f'data{col_postfix}'
                    ] = forecast_row[
                        f"{col_prefix_to_match}{col_postfix}"
                    ].values[0].astype(np_int) // 10**9
                else:
                    missing_val_data_frame.loc[
                        index, f'data{col_postfix}'
                    ] = forecast_row[
                        f"{col_prefix_to_match}{col_postfix}"].values[0]
    return missing_val_data_frame


def get_metrics(
    y_true,
    y_pred,
    allowed_margin_of_error: float = 0.05,
    penalize_negative_numbers: bool = False,
    round_result: bool = False,
    round_to_decimals: int = 2
):
    """Calculates the performance of a regression method
     using scikit-learn's regression metrics.
    
    Arguments:
        y_true -- Truth values
        y_pred -- Predicted values
    
    Keyword Arguments:
        allowed_margin_of_error {float} -- percentage allowed margin of error. If the predicted value is within the
        given margin of error, it will count as correct. (default: {0.05})
        penalize_negative_numbers {bool} -- if True, negative numbers won't be counted
        towards the accuracy score.
        round_result {bool} -- if True, numbers will get rounded (default: {False})
        round_to_decimals {int} -- rounds numbers to given decimals (default: {4})
    
    Returns:
        {dict} -- A dictionary of regression metrics
    """
    # https://scikit-learn.org/stable/modules/classes.html#regression-metrics
    from sklearn.metrics import (
        explained_variance_score,
        max_error,
        mean_absolute_error,
        mean_squared_error,
        r2_score
    )
    highest_value = max(y_true)
    # print(f"highest val is {highest_value}")
    allowed_margin = (highest_value * 0.05)
    is_in_range = 0
    y_true_list = y_true.tolist()
    for index, value in enumerate(y_pred):
        true_val = y_true_list[index]
        # print(f"true val is {true_val} and predicted val is {value}")
        if (true_val - allowed_margin <= value and value <= true_val + allowed_margin):
            if penalize_negative_numbers:
                # print(f"{value} is bigger than 0?")
                if true_val == 0:
                    # print(f"{value > 0}")
                    is_in_range += 0.1
                else:
                    is_in_range += 1
            else:
                is_in_range += 1

    variance_score = explained_variance_score(y_true, y_pred)
    max_residual_error = max_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    # returns RMSE value if squared boolean is False
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    r2_val = r2_score(y_true, y_pred)
    accuracy = is_in_range / len(y_true)

    if round_result:
        allowed_margin = round(allowed_margin, round_to_decimals)
        variance_score = variance_score.round(round_to_decimals)
        max_residual_error = max_residual_error.round(round_to_decimals)
        mae = mae.round(round_to_decimals)
        rmse = rmse.round(round_to_decimals)
        r2_val = r2_val.round(round_to_decimals)
        accuracy = round((accuracy * 100), round_to_decimals)

    return {
        'allowed margin is': allowed_margin,
        'explained variance regression score, closer to 1.0 is better': variance_score,
        # largest absolute difference between predicted and truth value
        'max residual error': max_residual_error,
        'mean absolute error': mae,  # average difference
        # average difference root squared, detects outliers
        'root mean squared error': rmse,
        'r^2 score': r2_val,
        'accuracy': f"{accuracy}%"  # custom accuracy matrix
    }


def clean_dataframe(data_frame: DataFrame):
    # Floor seconds
    data_frame['created_date'] = data_frame['created_date'].map(
        lambda x: x.replace(second=0))
    # Count the number of clients that are connected when the office is not open, then substract the amount to create
    # a sparser distribution.
    pass


def get_future_timestamps(day_of_week: int = 0, timestamp: int = 3600, number_of_timestamps: int = 168):
    """Calculates the future timestamps from a given day of the week.
    
    Keyword Arguments:
        day_of_week {int} -- calculate next day of the week 
        (0-6, where 0 is monday and 6 is sunday)  (default: {0})
        timestamp {int} -- timestamp (default: {3600})
        number_of_timestamps {int} -- how many timestamps to calculate 
        (default is 1 week worth of timestamps) (default: {168})
    
    Returns:
        [list] -- Returns a list of timestamps
    """
    import datetime as dt
    future_timestamps = []
    today = dt.date.today()
    next_day_of_week = today + dt.timedelta(
        (day_of_week - today.weekday()) % 7)
    timestamp_next_day_of_week = int(
        (next_day_of_week - dt.date(1970, 1, 1)).total_seconds())

    accumulative_timestamp = 0
    for index in range(number_of_timestamps):
      future_timestamps.append(
          timestamp_next_day_of_week + accumulative_timestamp)
      # print(dt.datetime.utcfromtimestamp(timestamp_next_day_of_week + accumulative_timestamp)) # converts timestamp to utc datetime
      accumulative_timestamp += timestamp
    return future_timestamps


def get_last_month():
    import datetime as dt
    prev_month_end = dt.date.today().replace(day=1) - dt.timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)
    return {
        'month_start': prev_month_start,
        'month_end': prev_month_end
    }


def get_past_weeks(number_of_weeks: int = 3):
    import datetime as dt
    start_week = dt.date.today() - dt.timedelta(days=dt.date.today().weekday(),
                                                weeks=number_of_weeks)
    end_week = dt.date.today() - dt.timedelta(days=dt.date.today().weekday())
    return start_week, end_week


# 30T of 1H voor de beste grafiek
# 3H voor de voorspelling vanwege de weatherforecast data
TIME_UNIT = '3H'

start_date = dt.strptime(("2019-10-01").split(' ')[0], '%Y-%m-%d')
# end_date_1 = dt.strptime(("2019-12-10").split(' ')[0], '%Y-%m-%d')

data_source_df = DataFrame(
    list(DataSourceData.select().where(
        DataSourceData.created_date >= start_date,
        # DataSourceData.created_date <= end_date_1,
        DataSourceData.data_source_id == 2).dicts()))

wrongly_reported_data_source_df = DataFrame(
    list(DataSourceData.select().where(
        DataSourceData.data_source_id == 1).dicts()))

hourly_weather_query = Weather.select().where(
    Weather.created_date >= start_date,
    # Weather.created_date <= end_date_1,/
    Weather.weather_forecast_type == Forecast.HOURLY)

hourly_weather_array = []
for weather in hourly_weather_query:
    hourly_weather_array.append(model_to_dict(weather, recurse=False))

hourly_weather_df = DataFrame(hourly_weather_array)

weekly_weather_query = Weather.select().where(
    Weather.weather_forecast_type == Forecast.FIVE_DAYS_THREE_HOUR)

weekly_weather_array = []
for weather in weekly_weather_query:
    weekly_weather_array.append(model_to_dict(weather, recurse=False))

weekly_weather_df = DataFrame(weekly_weather_array)
data_source_df = data_source_df[(
    data_source_df['created_date'] >= start_date)]
# flooring the seconds
data_source_df['created_date'] = data_source_df['created_date'].map(
    lambda x: x.replace(second=0))

wrongly_reported_data_source_df = wrongly_reported_data_source_df[(
    wrongly_reported_data_source_df['created_date'] >= start_date
)]

wrongly_reported_data_source_df['created_date'] = wrongly_reported_data_source_df['created_date'].map(
    lambda x: x.replace(second=0))

weekly_filter = "{\"5_days_3_hour_forecast\": list[].{dt: dt, main: main,"\
    "weather: {main: weather[0].main, description: weather[0].description },"\
    "clouds: clouds, wind: wind, rain: rain}}"

weekly_weather_df = filter_column_json_data(weekly_weather_df, 'data',
                                            weekly_filter)

weekly_weather_df = flatten_json_data_in_column(weekly_weather_df, 'data')
weekly_weather_df = unpack_json_array(weekly_weather_df,
                                      'data_5_days_3_hour_forecast')

weekly_weather_df.columns = map(_rename_columns, weekly_weather_df.columns)
weekly_weather_forecast_df = flatten_json_data_in_column(
    weekly_weather_df, 'data', 40)
weekly_weather_forecast_df = unix_to_datetime(weekly_weather_forecast_df)

# set_option('display.max_rows', None)

hourly_filter = "{dt: dt,  weather: {main: weather[0].main,"\
    "description: weather[0].description}, main: main, wind: wind"\
    ", rain: rain, clouds: clouds}"

hourly_weather_df = filter_column_json_data(hourly_weather_df, 'data',
                                            hourly_filter)

hourly_weather_df = flatten_json_data_in_column(hourly_weather_df, 'data')
hourly_weather_df['created_date'] = hourly_weather_df['created_date'].map(
    lambda x: x.replace(second=0)
)

wrongly_reported_data_source_df['created_date'] = wrongly_reported_data_source_df['created_date'].map(
    lambda x: x.replace(second=0)
)
# Remove data_rain column as it does not contain any data
del hourly_weather_df['data_rain']

# Subtract the 8 devices/clients that are always connected, it needs to be a variable instead of a static constant.
# Since the number of always connected clients may vary (for example since december there are only 7 always connected clients)
data_source_df['no_of_clients'] = data_source_df['no_of_clients'] - 8
data_source_df.loc[data_source_df['no_of_clients'] < 0, 'no_of_clients'] = 0
merged_df = data_source_df.merge(
    hourly_weather_df, on='created_date', how='left')

wrongly_reported_data_source_df['no_of_clients'] = wrongly_reported_data_source_df['no_of_clients'] - 8
wrongly_reported_data_source_df.loc[wrongly_reported_data_source_df['no_of_clients']
                                    < 0, 'no_of_clients'] = 0
wrongly_reported_data_source_df.loc[wrongly_reported_data_source_df['no_of_clients']
                                    > 1000, 'no_of_clients'] = 100

# Clean dataframe
merged_df = drop_columns_with_postfix(merged_df)
merged_df.rename(
    columns={'id_x': 'id', 'data_source_x': 'data_source'}, inplace=True)

# Subset of hourly_weather_df for weather labels
weather_description_labels_df = hourly_weather_df[[
    'created_date',
    'data_weather.main',
    'data_weather.description']]

weather_description_labels_df = weather_description_labels_df.resample(
    TIME_UNIT, on='created_date').agg({
        # sort the list to get the top 3 most occurrence
        'data_weather.main': lambda x: sorted(x.value_counts().keys()[0:3].tolist()),
        'data_weather.description': lambda x: sorted(x.value_counts().keys()[0:3].tolist())
    }).reset_index()
weather_description_labels_df['day_of_week'] = weather_description_labels_df['created_date'].dt.day_name()
# weather_description_labels_df['is_workday'] = weather_description_labels_df['day_of_week'].apply(
#     lambda x: item_in_list(
#         x, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
# )
weather_description_labels_df['is_weekend'] = weather_description_labels_df['day_of_week'].apply(
    lambda x: item_in_list(x, ['Saturday', 'Sunday'])
)

weather_description_labels_df['data_weather.description'] = weather_description_labels_df['data_weather.description'].apply(
    lambda x: convert_list_to_string(x))

weather_description_labels_df['data_weather.main'] = weather_description_labels_df['data_weather.main'].apply(
    lambda x: convert_list_to_string(x))

weather_description_labels_df['date_hour'] = weather_description_labels_df['created_date'].dt.hour

# Subset of hourly_weather_df for sum of rain
rain_df = hourly_weather_df[['created_date', 'data_rain.1h']]
rain_df = rain_df.resample(TIME_UNIT, on='created_date').sum().reset_index()
rain_df = rain_df.rename(
    {'data_rain.1h': f"data_rain.{TIME_UNIT.lower()}"}, axis=1)

# Calculate the mean of all the values
merged_df = merged_df.resample(
    TIME_UNIT, on='created_date').mean().reset_index()
merged_df = merged_df.merge(
    weather_description_labels_df, on='created_date', how='left')
merged_df = merged_df.merge(
    rain_df, on='created_date', how='left')
merged_df['data_source'].round(0)
merged_df['no_of_clients'].round(2)
# Drop columns
del merged_df['id']
del merged_df['data_rain.1h']

# fill in weather data using known forecast data
filled_data_frame = fill_missing_values_using_forecast(
    merged_df[merged_df['data_main.temp'].isnull()],
    weekly_weather_forecast_df, 'created_date')

merged_df = merged_df.combine_first(filled_data_frame)
label_encoder = LabelEncoder()


def iteration_1(input_dataframe):
    # Label encoder used to transform the different categories to a numeric representation
    for item in ['data_weather.main', 'data_weather.description', 'day_of_week', 'is_weekend']:
        input_dataframe[item] = label_encoder.fit_transform(
            input_dataframe[item])
    print(
        f"{len(merged_df[merged_df['data_main.temp'].isnull()])}/{len(merged_df)} is null")
    # print(f"input_dataframe after using label_encoder: \n {input_dataframe.info()}")
    print('data frame where temp is empty after filling')
    print(
        f"{len(input_dataframe[input_dataframe['data_main.temp'].isnull()])}/{len(input_dataframe)} is null")

    # Drop rows when it does not contain any value in column 'no_of_clients'
    input_dataframe = input_dataframe.dropna(subset=['no_of_clients'])

    figure = make_subplots()
    figure.add_trace(
        go.Bar(
            x=input_dataframe['created_date'],
            y=input_dataframe['no_of_clients'],
            name="Number of clients reported by PI",
            marker=go.bar.Marker(
                color='rgb(63, 81, 181)'
            )
        ),
        # secondary_y=True,
    )

    figure.add_trace(
        go.Scatter(
            x=input_dataframe['created_date'],
            y=input_dataframe['data_main.temp'],
            name="Temperature in Celcius",
            # marker_color='Purple',
            # marker=go.bar.Marker(
            #                color='rgb(63, 81, 181)'
            #     )
        ),
        # secondary_y=False,
    )

    # figure.add_trace(
    #     go.Scatter(
    #         x=wrongly_reported_data_source_df['created_date'],
    #         y=wrongly_reported_data_source_df['no_of_clients'],
    #         name='Number of clients reported by Unifi Cloud',
    #     ),
    #     secondary_y=True,
    # )

    # figure.update_yaxes(title_text="Number of clients", secondary_y=True)
    # figure.update_yaxes(title_text="Temperature in celcius", secondary_y=False)
    figure.update_layout(
        showlegend=True,
        legend_orientation="h",
        legend=dict(x=0, y=1.1))

    # figure.show()
    merged_df_dropped_col = input_dataframe
    prediction_df = input_dataframe  # create a copy of the merged df for prediction
    # reset index to get created_Date column
    prediction_df = prediction_df.reset_index()
    for item in ['data_source', 'created_date', 'data_main.feels_like', 'data_rain.3h_x', 'data_rain.3h_y', 'data_dt']:
        try:
            del merged_df_dropped_col[item]
        except KeyError:
            print(f"key {item} does not exist.")

    for item in ['index', 'data_source', 'data_main.feels_like', 'data_rain.3h_x', 'data_rain.3h_y', 'data_dt']:
        try:
            del prediction_df[item]
        except KeyError:
            print(f"key {item} does not exist.")

    # print(merged_df_dropped_col.corr())

    # merged_df_dropped_col['empty_col'] = ""

    # print(input_dataframe.corr())
    # print(input_dataframe.info())
    # hovertext = input_dataframe.corr().round(4)
    # heat = go.Heatmap(
    #     z=input_dataframe.corr(),
    #     x=list(input_dataframe),
    #     y=list(input_dataframe),
    #     xgap=1, ygap=1,
    #     # colorscale=px.colors.sequential.Plotly3,
    #     colorbar_thickness=20,
    #     colorbar_ticklen=3,
    #     text=input_dataframe.corr().values,
    #     hovertext=hovertext,
    #     hoverinfo='text',
    # )

    # summary = merged_df_dropped_col.describe()
    # print(f"The summary is \n {summary.transpose()}")

    # print(f"Dataframe information: \n {merged_df_dropped_col.info()}")
    hovertext = merged_df_dropped_col.corr().round(4)
    # print(f"column headers are \n{list(summary)}")

    # Unable to show value of the correlation in the cell using Heatmap function
    heat = go.Heatmap(
        z=merged_df_dropped_col.corr(),
        x=list(merged_df_dropped_col),
        y=list(merged_df_dropped_col),
        xgap=1, ygap=1,
        # colorscale=px.colors.sequential.Plotly3,
        colorbar_thickness=20,
        colorbar_ticklen=3,
        text=merged_df_dropped_col.corr().values,
        hovertext=hovertext,
        hoverinfo='text',
    )

    # test_df = input_dataframe.groupby(input_dataframe['created_date'].map(lambda t: t.hour))
    # test_df = input_dataframe.groupby(input_dataframe['created_date'].to_period('S'))
    # print(test_df)

    # layout = go.Layout(
    #     xaxis_showgrid=False,
    #     yaxis_showgrid=False)
    # #     yaxis_autorange='reversed')
    # figure_2 = go.Figure(data=[heat], layout=layout)
    # figure_2.show()

    # print(input_dataframe[['no_of_clients', 'day_of_week']].corr())
    # print(input_dataframe.corr())

    # corr = input_dataframe.corr()
    # corr.style.background_gradient(cmap='coolwarm').set_precision(2)
    # corr.show()

    # temp = merged_df_dropped_col.mask(np.tril(np.ones(merged_df_dropped_col.shape)).astype(np.bool))

    # figure_3 = ff.create_annotated_heatmap(
    #     merged_df_dropped_col.corr().values,
    #     x=list(merged_df_dropped_col), y=list(merged_df_dropped_col),
    #     annotation_text=merged_df_dropped_col.corr().values.round(4))

    # figure_3.show()

    # figure_4 = ff.create_annotated_heatmap(
    #     merged_df_dropped_col[merged_df_dropped_col.columns[:]].corr()[
    #         ['no_of_clients']][:].values,
    #     x=list(merged_df_dropped_col[merged_df_dropped_col.columns[:]].corr()[
    #            ['no_of_clients']][:]),
    #     y=list(merged_df_dropped_col),
    #     annotation_text=merged_df_dropped_col[merged_df_dropped_col.columns[:]].corr()[
    #         ['no_of_clients']][:].values.round(4)
    # )

    # figure_4.update_layout(
    #     title="Correlation with NaN's"
    # )
    # figure_4.show()

    # prediction_df[['data_weather.main', 'data_weather.description', 'day_of_week', 'is_weekend']] = prediction_df[['data_weather.main', 'data_weather.description', 'day_of_week', 'is_weekend']].apply(
    #     lambda x: x.astype('float')
    # )

    # Extra cleaning of data due to regression not accepting the dataframe if it contains NaN values
    # replace NaN values with -1
    prediction_df = prediction_df.fillna(0)

    # print(prediction_df.info())
    summary = prediction_df.describe()
    print(f"The summary is \n {summary.transpose()}")

    # Used for printing underscores in LaTeX
    stringified_list = ", ".join(list(summary))
    print(f"Length of columns are {len(list(summary))}")
    print(stringified_list.replace("_", "\_"))

    # split dataset in 80 train and 20 test, do not shuffle as the date is important
    train, test = train_test_split(
        prediction_df, test_size=0.25, shuffle=False)
    print(f"training size is {len(train)}")
    print(f"test size is {len(test)}")
    # select range to exclude column created_date
    train_X = train.iloc[:, range(1, 16)]
    test_X = test.iloc[:, range(1, 16)]

    # the number of clients that are being predicted
    train_y = train.iloc[:, 16]
    test_y = test.iloc[:, 16]
    reg = LinearRegression()
    reg.fit(train_X, train_y)

    pred_y = reg.predict(test_X)

    scaler = StandardScaler()  # using scaler improves the svr modeling
    train_X_scaled = scaler.fit_transform(train_X)

    # #############################################################################
    # # Fit regression model

    # SVR parameters from https://scikit-learn.org/stable/auto_examples/plot_kernel_ridge_regression.html
    # for kernel in ['rbf', 'linear', 'poly']:
    # for kernel in ['rbf', 'linear']:
    #     svr = GridSearchCV(SVR(kernel=kernel, gamma=0.1),
    #                        param_grid={"C": [1e0, 1e1, 1e2, 1e3],
    #                                    "gamma": np.logspace(-2, 2, 5)})
    #     svr = svr.fit(train_X_scaled, train_y)
    #     print(f"Best estimator found by grid search for kernel {kernel} is:")
    #     print(svr.best_estimator_)

    # # parameters from https://scikit-learn.org/stable/auto_examples/exercises/plot_cv_diabetes.html
    # alphas = np.logspace(-4, -0.5, 30)
    # tuned_parameters = [{'alpha': alphas}]

    # parameters = { 'alpha': [1e-15, 1e-10, 1e-8, 1e-4, 1e-3, 1e-2, 1, 5, 10, 20]}
    # n_folds = 5
    # print('running gridsearch for lasso, ridge and elastic')
    # lasso = GridSearchCV(Lasso(selection='random', tol=1, max_iter=1000),
    #                      parameters, cv=n_folds, refit=False)

    # lasso = lasso.fit(train_X, train_y)
    # print(
    #     f"best index is {lasso.best_index_}, parameters are {lasso.best_params_} and score is {lasso.best_score_}")

    # # lasso_cv = LassoCV(tol=1, max_iter=1000, cv=n_folds)
    # # print(f"best alpha using lasso cv is {lasso_cv.alphas}")
    # ridge_reg = Ridge()

    # ridge = GridSearchCV(Ridge(), parameters, cv=n_folds)
    # ridge = ridge.fit(train_X, train_y)
    # print("Best estimator found by grid search for Ridge is:")
    # print(
    #     f"best index is {ridge.best_index_}, parameters are {ridge.best_params_} and score is {ridge.best_score_}")

    # elastic = GridSearchCV(ElasticNet(tol=1, max_iter=1000), parameters, cv=n_folds)
    # elastic = elastic.fit(train_X, train_y)
    # print("Best estimator found by grid search for ElasticNet is:")
    # print(
    #     f"best index is {elastic.best_index_}, parameters are {elastic.best_params_} and score is {ridge.best_score_}")

    # exit(0)
    # #############################################################################

    # some explanation of the alpha factor of ridge and lasso (and elastic)
    # https://www.analyticsvidhya.com/blog/2016/01/complete-tutorial-ridge-lasso-regression-python/#four
    # svr_rbf = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=.1)
    svr_rbf = SVR(C=1000.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=1.0,
                  kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
    # svr_lin = SVR(kernel='linear', C=100, gamma='auto')
    svr_lin = SVR(C=100.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=0.01,
                  kernel='linear', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
    # svr_poly = SVR(kernel='poly', C=100, gamma='auto', degree=3, epsilon=.1,
    #                coef0=1)
    svr_poly = SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=0.1,
                   kernel='poly', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
    # svrs = [svr_rbf, svr_lin, svr_poly]
    svrs = [svr_rbf, svr_lin]
    kernel_label = ['Radial basis function (RBF)', 'Linear', 'Polynomial']

    lasso = Lasso(0.0001, tol=1)
    ridge = Ridge(5)
    elastic = ElasticNet(0.01, tol=1)

    other_methods = [lasso, ridge, elastic]
    other_label = ['Lasso', 'Ridge Regression', 'ElasticNet']

    # # The coefficients
    # print('Coefficients: \n', reg.coef_)
    # # The mean squared error
    # print('Mean squared error: %.2f'
    #       % mean_squared_error(test_y, pred_y))
    # # The coefficient of determination: 1 is perfect prediction
    # print('Coefficient of determination (R^2): %.2f'
    #       % r2_score(test_y, pred_y))
    # print(f"mean of no_of_clients {np.mean(input_dataframe['no_of_clients'])}")
    # print(
    #     f"standard deviation of no_of_clients is {np.std(input_dataframe['no_of_clients'])}")

    print("---------- Regression metrics ----------")
    print('---------- LinearRegression() ----------')
    for k, v in get_metrics(test_y, pred_y, round_result=True).items():
        print(f"{k}: {v}")

    test_X_scaled = scaler.fit_transform(test_X)

    for ix, svr in enumerate(svrs):
        # train_y_scaled = scaler.fit_transform(train_y)
        # test_y_scaled = scaler.fit_transform(test_y)
        pred_y_svr = svr.fit(train_X_scaled, train_y).predict(test_X_scaled)
        print(f"---------- SVR {kernel_label[ix]} ----------")
        for k, v in get_metrics(test_y, pred_y_svr, round_result=True).items():
            print(f"{k}: {v}")

    for ix, mthd in enumerate(other_methods):
        pred_y_mthd = mthd.fit(train_X, train_y).predict(test_X)
        print(f"---------- Method {other_label[ix]} ----------")
        for k, v in get_metrics(test_y, pred_y_mthd, round_result=True).items():
            print(f"{k}: {v}")
    # exit(0)
    # print(f"confusion matrix \n {confusion_matrix(test_y, pred_y)}")

    figure_5 = make_subplots()
    figure_5.add_trace(
        go.Scatter(
            x=prediction_df['created_date'],
            y=prediction_df['no_of_clients'],
            name="Number of clients reported by PI",
            marker_color='rgb(63, 81, 181)'
            #    marker=go.bar.Marker(
            #                color='rgb(63, 81, 181)'
            #     )
        ),
        # secondary_y=True,
    )

    figure_5.add_trace(
        go.Scatter(
            x=test.iloc[:, 0],  # select created_date column
            y=pred_y,
            name="Linear regression (OLS)",
            marker_color='Red'
        ),
        # secondary_y=True,
    )

    for ix, svr in enumerate(svrs):
        figure_5.add_trace(
            go.Scatter(
                x=test.iloc[:, 0],
                y=svr.fit(train_X_scaled, train_y).predict(test_X_scaled),
                name=f"SVR {kernel_label[ix]}"
            )
        )

    for ix, mthd in enumerate(other_methods):
        figure_5.add_trace(
            go.Scatter(
                x=test.iloc[:, 0],
                y=mthd.fit(train_X, train_y).predict(test_X),
                name=f"{other_label[ix]}"
            )
        )

    # figure_5.add_trace(
    #     go.Scatter(
    #         x=prediction_df['created_date'],
    #         y=prediction_df['data_main.temp'],
    #         name="Temperature in Celcius",
    #     ),
    #     # secondary_y=True,
    # )

    figure_5.update_layout(
        showlegend=True,
        legend_orientation="h",
        legend=dict(x=0, y=1.1))

    figure_5.show()
    # print('dataframe info is:')
    # print(merged_df_dropped_col.info())

    # see https://stats.stackexchange.com/questions/101130/correlation-coefficient-for-sets-with-non-linear-correlation
    pearson_corr = merged_df_dropped_col[merged_df_dropped_col.columns[:]].corr()[
        'no_of_clients'][:].values
    spearman_corr = merged_df_dropped_col[merged_df_dropped_col.columns[:]].corr(
        method='spearman')['no_of_clients'][:].values
    kendall_corr = merged_df_dropped_col[merged_df_dropped_col.columns[:]].corr(
        method='kendall')['no_of_clients'][:].values
    corr_2d_array = np.array([pearson_corr, spearman_corr, kendall_corr])
    corr_2d_array = np.swapaxes(corr_2d_array, 0, 1)

    del prediction_df['created_date']
    correlation_figure = ff.create_annotated_heatmap(
        corr_2d_array,
        x=['pearson', 'spearman', 'kendall'],
        y=list(prediction_df),
        annotation_text=corr_2d_array.round(4),
    )

    correlation_figure.update_layout(
        title="Correlation with NaN's replaced"
    )

    correlation_figure.show()

    histo_figure = make_subplots()
    histo_figure.add_trace(
        go.Histogram(
            x=input_dataframe['no_of_clients'],
            # y=input_dataframe['no_of_clients'],
            xbins=dict(start=min(input_dataframe['no_of_clients']), size=1, end=max(
                input_dataframe['no_of_clients']))
        )
    )

    histo_figure.update_xaxes(title_text='Number of clients')
    histo_figure.update_yaxes(title_text='Occurrence')
    histo_figure.show()

    qq = stats.probplot(input_dataframe['no_of_clients'])
    # qq = stats.probplot(input_dataframe['no_of_clients'], dist='lognorm', sparams=(1))
    x = np.array([qq[0][0][0], qq[0][0][-1]])

    qq_figure = make_subplots()
    qq_figure.add_trace(
        go.Scatter(
            x=qq[0][0],
            y=qq[0][1],
            mode='markers',
            showlegend=False
        )
    )

    qq_figure.add_trace(
        go.Line(
            x=x,
            y=qq[1][1] + qq[1][0] * x,
            showlegend=False
        )
    )

    qq_figure.update_layout(
        title='QQ plot'
    )
    qq_figure.update_xaxes(title_text='Quantiles')
    qq_figure.update_yaxes(title_text='Number of clients')
    qq_figure.show()

    # Normality test
    stat, p = stats.shapiro(input_dataframe['no_of_clients'])
    print(f"Shapiro-wilk test \n W={stat}, p-value={p}")
    alpha = 0.05
    if p > alpha:
        print('Sample looks Gaussian (fail to reject H0)')
    else:
        print('Sample does not look Gaussian (reject H0)')

    pair_plot_figure = px.scatter_matrix(merged_df_dropped_col)
    pair_plot_figure.update_layout(
        height=1200,
        # autosize=True,
    )
    # pair_plot_figure.update_yaxes(tickangle=-45) # only changes the upper left corner labels
    # pair_plot_figure.add_annotation(textangle=-90) # does not seem to change the y axis title
    # pair_plot_figure.update_traces(showlowerhalf=False)
    pair_plot_figure.show()
    # range_of_coef_sorted = Series(train.iloc[:, range(1, 15)].columns).sort_values()

    coeff_plot = make_subplots()
    coeff_plot.add_trace(
        go.Bar(
            y=Series(reg.coef_, train.iloc[:, range(
                1, 16)].columns).sort_values(),
            x=train.iloc[:, range(1, 16)].columns,
            text=Series(reg.coef_, train.iloc[:, range(
                1, 16)].columns).sort_values().round(2),
            textposition='auto'
        )
    )

    coeff_plot.update_layout(
        title="Coefficient Estimate"
    )
    coeff_plot.show()

    coeff_plot_2 = make_subplots()
    coeff_plot_2.add_trace(
        go.Bar(
            y=Series(svr_lin.coef_.ravel(), train.iloc[:, range(
                1, 16)].columns).sort_values(),
            x=train.iloc[:, range(1, 16)].columns,
            text=Series(svr_lin.coef_.ravel(), train.iloc[:, range(
                1, 16)].columns).sort_values().round(2),
            textposition='auto'
        )
    )

    coeff_plot_2.update_layout(
        title="Coefficient Estimate (SVR Linear)"
    )
    coeff_plot_2.show()

# iteration_1(merged_df)


def iteration_2(data_frame, time_unit):
    print(f"Dataframe using resampled data per {time_unit}")
    # Calculate the mean of all the values
    print(f"length of input dataframe is: {len(data_frame)}")
    start, end = get_past_weeks()
    print(f"{start}-{end}")
    data_frame = data_frame.resample(
        time_unit, on='created_date').mean().reset_index()
    data_frame['day_of_week'] = data_frame['created_date'].dt.day_name()
    data_frame['date_hour'] = data_frame['created_date'].dt.hour
    # data_frame['data_source'].round(0)
    data_frame['no_of_clients'].round(2)
    data_frame['is_weekend'] = data_frame['day_of_week'].apply(
        lambda x: item_in_list(x, ['Saturday', 'Sunday'])
    )
    del data_frame['id']
    del data_frame['data_source']
    print(data_frame)
    next_week_dataframe = DataFrame({'created_date': get_future_timestamps()})
    next_week_dataframe['created_date'] = to_datetime(
        next_week_dataframe['created_date'], unit='s')
    next_week_dataframe['day_of_week'] = next_week_dataframe['created_date'].dt.day_name()
    next_week_dataframe['date_hour'] = next_week_dataframe['created_date'].dt.hour
    next_week_dataframe['is_weekend'] = next_week_dataframe['day_of_week'].apply(
        lambda x: item_in_list(x, ['Saturday', 'Sunday'])
    )

    for item in ['day_of_week', 'is_weekend']:
        data_frame[item] = label_encoder.fit_transform(data_frame[item])

    for item in ['day_of_week', 'is_weekend']:
        next_week_dataframe[item] = label_encoder.fit_transform(
            next_week_dataframe[item])

    data_frame = data_frame.fillna(0)

    summary = data_frame.describe()
    print(f"The summary is \n {summary.transpose()}")

    # Used for printing underscores in LaTeX
    stringified_list = ", ".join(list(summary))
    print(f"Length of columns are {len(list(summary))}")
    print(stringified_list.replace("_", "\_"))

    # split dataset in 80 train and 20 test, do not shuffle as the date is important
    train, test = train_test_split(
        data_frame, test_size=0.25, shuffle=False)
    # select range to exclude column created_date
    train_X = train.iloc[:, range(2, 5)]
    test_X = test.iloc[:, range(2, 5)]
    future_X = next_week_dataframe.iloc[:, range(1, 4)]

    # the number of clients that are being predicted
    train_y = train.iloc[:, 1]
    test_y = test.iloc[:, 1]

    # linear regression (OLS)
    reg = LinearRegression()
    reg.fit(train_X, train_y)

    pred_y = reg.predict(test_X)

    scaler = StandardScaler()  # using scaler improves the svr modeling
    train_X_scaled = scaler.fit_transform(train_X)

    # #############################################################################
    # # Fit regression model

    # # SVR parameters from https://scikit-learn.org/stable/auto_examples/plot_kernel_ridge_regression.html
    # for kernel in ['rbf', 'linear']:
    #     svr = GridSearchCV(SVR(kernel=kernel, gamma=0.1),
    #                        param_grid={"C": [1e0, 1e1, 1e2, 1e3],
    #                                    "gamma": np.logspace(-2, 2, 5)})
    #     svr = svr.fit(train_X_scaled, train_y)
    #     print(f"Best estimator found by grid search for kernel {kernel} is:")
    #     print(svr.best_estimator_)

    # # parameters from https://scikit-learn.org/stable/auto_examples/exercises/plot_cv_diabetes.html
    # alphas = np.logspace(-4, -0.5, 30)
    # tuned_parameters = [{'alpha': alphas}]

    # parameters = { 'alpha': [1e-15, 1e-10, 1e-8, 1e-4, 1e-3, 1e-2, 1, 5, 10, 20]}
    # n_folds = 5

    # lasso = GridSearchCV(Lasso(selection='random', tol=1, max_iter=1000),
    #                      parameters, cv=n_folds, refit=False)

    # lasso = lasso.fit(train_X, train_y)
    # print("Best estimator found by grid search for Lasso is:")
    # print(
    #     f"best index is {lasso.best_index_}, parameters are {lasso.best_params_} and score is {lasso.best_score_}")

    # lasso_cv = LassoCV(tol=1, max_iter=1000, cv=n_folds)
    # # print(f"best alpha using lasso cv is {lasso_cv.alphas}")
    # ridge_reg = Ridge()

    # ridge = GridSearchCV(Ridge(), parameters, cv=n_folds)
    # ridge = ridge.fit(train_X, train_y)
    # print("Best estimator found by grid search for Ridge is:")
    # print(
    #     f"best index is {ridge.best_index_}, parameters are {ridge.best_params_} and score is {ridge.best_score_}")

    # elastic = GridSearchCV(ElasticNet(tol=1, max_iter=1000), parameters, cv=n_folds)
    # elastic = elastic.fit(train_X, train_y)
    # print("Best estimator found by grid search for ElasticNet is:")
    # print(
    #     f"best index is {elastic.best_index_}, parameters are {elastic.best_params_} and score is {ridge.best_score_}")

    # exit(0)
    # #############################################################################

    svr_rbf = SVR(C=100.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=1.0,
                  kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False)

    svr_lin = SVR(C=1000.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=0.01,
                  kernel='linear', max_iter=-1, shrinking=True, tol=0.001, verbose=False)

    svrs = [svr_rbf, svr_lin]
    kernel_label = ['Radial basis function (RBF)', 'Linear', 'Polynomial']

    lasso = Lasso(0.01, tol=1)
    ridge = Ridge(20)
    elastic = ElasticNet(0.01, tol=1)

    other_methods = [lasso, ridge, elastic]
    other_label = ['Lasso', 'Ridge Regression', 'ElasticNet']

    test_X_scaled = scaler.fit_transform(test_X)
    future_X_scaled = scaler.fit_transform(future_X)

    result = svr_rbf.fit(train_X_scaled, train_y).predict(future_X_scaled)
    # print(len(result))
    # print(len(next_week_dataframe['created_date']))
    next_week_dataframe['predicted_no_of_clients'] = result
    print(next_week_dataframe[['created_date', 'predicted_no_of_clients']])
    print(f"date range is \n{next_week_dataframe['created_date'].iloc[0]} - {next_week_dataframe['created_date'].iloc[-1]}")
    exit(0)

    print("---------- Regression metrics ----------")
    print('---------- LinearRegression() ----------')
    # for k, v in get_metrics(test_y, pred_y, round_result=True).items():
    #     print(f"{k}: {v}")

    for ix, svr in enumerate(svrs):
        # train_y_scaled = scaler.fit_transform(train_y)
        # test_y_scaled = scaler.fit_transform(test_y)
        pred_y_svr = svr.fit(train_X_scaled, train_y).predict(test_X_scaled)
        # pred_y_svr = svr.fit(train_X_scaled, train_y).predict(future_X_scaled)
        print(f"---------- SVR {kernel_label[ix]} ----------")
        for k, v in get_metrics(test_y, pred_y_svr, round_result=True).items():
            print(f"{k}: {v}")

    for ix, mthd in enumerate(other_methods):
        pred_y_mthd = mthd.fit(train_X, train_y).predict(test_X)
        # pred_y_mthd = mthd.fit(train_X, train_y).predict(future_X)
        print(f"---------- Method {other_label[ix]} ----------")
        for k, v in get_metrics(test_y, pred_y_mthd, round_result=True).items():
            print(f"{k}: {v}")

    figure_5 = make_subplots()
    figure_5.add_trace(
        go.Scatter(
            x=data_frame['created_date'],
            y=data_frame['no_of_clients'],
            name="Number of clients reported by PI",
            marker_color='rgb(63, 81, 181)'
            #    marker=go.bar.Marker(
            #                color='rgb(63, 81, 181)'
            #     )
        ),
        # secondary_y=True,
    )

    figure_5.add_trace(
        go.Scatter(
            x=test.iloc[:, 0],  # select created_date column
            # x=next_week_dataframe.iloc[:, 0]
            y=pred_y,
            name="Linear regression (OLS)",
            marker_color='Red'
        ),
        # secondary_y=True,
    )

    for ix, svr in enumerate(svrs):
        figure_5.add_trace(
            go.Scatter(
                # x=test.iloc[:, 0],
                x=next_week_dataframe.iloc[:, 0],
                y=svr.fit(train_X_scaled, train_y).predict(future_X_scaled),
                name=f"SVR {kernel_label[ix]}"
            )
        )

    for ix, mthd in enumerate(other_methods):
        figure_5.add_trace(
            go.Scatter(
                # x=test.iloc[:, 0],
                x=next_week_dataframe.iloc[:, 0],
                y=mthd.fit(train_X, train_y).predict(future_X),
                name=f"{other_label[ix]}"
            )
        )

    # figure_5.add_trace(
    #     go.Scatter(
    #         x=prediction_df['created_date'],
    #         y=prediction_df['data_main.temp'],
    #         name="Temperature in Celcius",
    #     ),
    #     # secondary_y=True,
    # )

    figure_5.update_layout(
        showlegend=True,
        legend_orientation="h",
        legend=dict(x=0, y=1.1))

    figure_5.show()

    pearson_corr = data_frame[data_frame.columns[:]].corr()[
        'no_of_clients'][:].values
    spearman_corr = data_frame[data_frame.columns[:]].corr(
        method='spearman')['no_of_clients'][:].values
    kendall_corr = data_frame[data_frame.columns[:]].corr(
        method='kendall')['no_of_clients'][:].values
    corr_2d_array = np.array([pearson_corr, spearman_corr, kendall_corr])
    corr_2d_array = np.swapaxes(corr_2d_array, 0, 1)

    # print(corr_2d_array)

    del data_frame['created_date']
    correlation_figure = ff.create_annotated_heatmap(
        corr_2d_array,
        x=['pearson', 'spearman', 'kendall'],
        y=list(data_frame),
        annotation_text=corr_2d_array.round(4),
    )

    correlation_figure.update_layout(
        title="Correlation with NaN's replaced"
    )

    correlation_figure.show()

    coeff_plot = make_subplots()
    coeff_plot.add_trace(
        go.Bar(
            y=Series(reg.coef_, train.iloc[:, range(
                2, 5)].columns).sort_values(),
            x=train.iloc[:, range(2, 5)].columns,
            text=Series(reg.coef_, train.iloc[:, range(
                2, 5)].columns).sort_values().round(2),
            textposition='auto'
        )
    )

    coeff_plot.update_layout(
        title="Coefficient Estimate"
    )
    coeff_plot.show()

    coeff_plot_2 = make_subplots()
    coeff_plot_2.add_trace(
        go.Bar(
            y=Series(svr_lin.coef_.ravel(), train.iloc[:, range(
                2, 5)].columns).sort_values(),
            x=train.iloc[:, range(2, 5)].columns,
            text=Series(svr_lin.coef_.ravel(), train.iloc[:, range(
                2, 5)].columns).sort_values().round(2),
            textposition='auto'
        )
    )

    coeff_plot_2.update_layout(
        title="Coefficient Estimate (SVR RBF)"
    )
    coeff_plot_2.show()
    pass

def test_retrieve_dataframe_database():
    import datetime as dt
    today = dt.date.today()
    print(today)
    print(f"striped time {today.strftime('%Y-%m-%d')}")
    result = CrowdForecast.get(
        CrowdForecast.prediction_start_date == '2020-01-22'
    )
    # result = CrowdForecast.get_by_id(1)
    print(result.prediction_data)
    dataframe = read_json(result.prediction_data)
    dataframe['created_date'] = to_datetime(
            dataframe['created_date'], unit='ms')
    print(dataframe)
    pass

test_retrieve_dataframe_database()
# iteration_1(merged_df)
# iteration_2(data_source_df, '1H')

