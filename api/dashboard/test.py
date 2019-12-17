import os as _os
from datetime import datetime as dt
from enum import Enum

from numpy import int as np_int
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dotenv import load_dotenv as _load_dotenv
from pandas import DataFrame, Series, set_option, to_datetime
from pandas.io.json import json_normalize
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, MySQLDatabase, PrimaryKeyField)
from playhouse.mysql_ext import JSONField
from playhouse.shortcuts import model_to_dict

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
        return 1
    else:
        return 0


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
        # print(list(data_frame.loc[[idx - 1]]))
        return data_frame.loc[[idx - 1]]
    else:
        # print(list(data_frame.loc[[idx]]))
        return data_frame.loc[[idx]]


def fill_missing_values_using_forecast(
        missing_val_data_frame: DataFrame,
        forecast_data_frame: DataFrame,
        column_name: str):
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


TIME_UNIT = '3H'

data_source_df = DataFrame(
    list(DataSourceData.select().where(
        DataSourceData.data_source_id == 2).dicts()))

start_date = dt.strptime(("2019-11-08").split(' ')[0], '%Y-%m-%d')

hourly_weather_query = Weather.select().where(
    Weather.created_date >= start_date,
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

## Date filter causes an odd behaviour, causing the resulting temperature to be NaN values
# print(f'size of hourly_weather_df before filtering is {hourly_weater_df.size}')
# hourly_weater_df = hourly_weater_df[(
#     hourly_weater_df['created_date'] >= start_date
# )]
# print(f'size of hourly_weather_df after filtering is {hourly_weater_df.size}')
# # print(hourly_weater_df.tail)
# print(list(hourly_weater_df))
weekly_filter = "{\"5_days_3_hour_forecast\": list[].{dt: dt, main: main,"\
    "weather: {main: weather[0].main, description: weather[0].description },"\
    "clouds: clouds, wind: wind, rain: rain}}"

# print('before weekly filter')
# print(weekly_weather_df.iloc[0])
weekly_weather_df = filter_column_json_data(weekly_weather_df, 'data',
                                            weekly_filter)
# print('after weekly filter')
# print(weekly_weather_df.iloc[0])
weekly_weather_df = flatten_json_data_in_column(weekly_weather_df, 'data')
# print(weekly_weather_df)
# weekly_weather_df.pipe(
#     lambda x: x.drop('data.5_days_3_hour_forecast', 1).join(
#         x['data.5_days_3_hour_forecast'].apply(lambda y: Series(merge(y)))
#     )
# )

# print('before splitting data_5_days_3_hour_forecast')
# print(weekly_weather_df)

# Flattens the json array that resides in the specified column and removes it
# after it is done

# weekly_weather_df = weekly_weather_df['data_5_days_3_hour_forecast'].apply(
#     Series).merge(weekly_weather_df, left_index=True,
#                   right_index=True).drop(['data_5_days_3_hour_forecast'],
#                                          axis=1)

weekly_weather_df = unpack_json_array(weekly_weather_df,
                                      'data_5_days_3_hour_forecast')

# print('after splitting data_5_days_3_hour_forecast')
# print(weekly_weather_df)
# weekly_weather_df = weekly_weather_df.rename(columns=_rename_column)
weekly_weather_df.columns = map(_rename_columns, weekly_weather_df.columns)
# df = weekly_weather_df.iloc[[0]]
# print(list(weekly_weather_df))
weekly_weather_forecast_df = flatten_json_data_in_column(
    weekly_weather_df, 'data', 40)
weekly_weather_forecast_df = unix_to_datetime(weekly_weather_forecast_df)
# weather_description_labels_df['day_of_week'] = weather_description_labels_df['created_date'].dt.day_name()
set_option('display.max_rows', None)
# print(flatest_df.iloc[-1])
# print(weekly_weather_forecast_df.head)
print('----------------- looking for value -----------------')
print(_find_value_near_datetime(weekly_weather_forecast_df, 'created_date',
                                dt.strptime(("2019-11-17").split(' ')[0], '%Y-%m-%d')))

hourly_filter = "{dt: dt,  weather: {main: weather[0].main,"\
    "description: weather[0].description}, main: main, wind: wind"\
    ", rain: rain, clouds: clouds}"

# print('before hourly filter')
# print(hourly_weater_df.iloc[0])
hourly_weather_df = filter_column_json_data(hourly_weather_df, 'data',
                                            hourly_filter)
# print('after hourly filter')
# print(hourly_weater_df.iloc[0])
hourly_weather_df = flatten_json_data_in_column(hourly_weather_df, 'data')
# hourly_weater_df["created_date"] = hourly_weater_df["created_date"].round("S")
hourly_weather_df['created_date'] = hourly_weather_df['created_date'].map(
    lambda x: x.replace(second=0))
# print('after hourly flatten')
# print(hourly_weater_df.iloc[0])
# print(hourly_weater_df.loc[[hourly_weater_df['id'] == 5674], ['id', 'created_date', 'data_main.temp']])
# print('------------------ print where id is 5674')
# print(hourly_weather_df.query("id == 5674")[
#       ['id', 'created_date', 'data_main.temp']])
# print(hourly_weather_df.head)
# Remove data_rain column as it does not contain any data
del hourly_weather_df['data_rain']
# print(hourly_weather_df['data_rain.S'].unique())
# print(f"wind gust is {hourly_weather_df['data_wind.gust'].unique()}")
# print(f"wind degree is {hourly_weather_df['data_wind.deg'].unique()}")
# print(hourly_weather_df['data_weather.main'].unique())
# print(hourly_weather_df.isna().any())

# Subtract the 8 devices/clients that are always connected
data_source_df['no_of_clients'] = data_source_df['no_of_clients'] - 8
data_source_df.loc[data_source_df['no_of_clients'] < 0, 'no_of_clients'] = 0
merged_df = data_source_df.merge(
    hourly_weather_df, on='created_date', how='left')
# print(list(merged_df))

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
        'data_weather.main': lambda x: sorted(x.value_counts().keys()[0:3].tolist()),
        'data_weather.description': lambda x: sorted(x.value_counts().keys()[0:3].tolist())
    }).reset_index()
weather_description_labels_df['day_of_week'] = weather_description_labels_df['created_date'].dt.day_name()
weather_description_labels_df['is_weekend'] = weather_description_labels_df['day_of_week'].apply(
    lambda x: item_in_list(x, ['Saturday', 'Sunday'])
)

weather_description_labels_df['data_weather.description'] = weather_description_labels_df['data_weather.description'].apply(
    lambda x: convert_list_to_string(x))

weather_description_labels_df['data_weather.main'] = weather_description_labels_df['data_weather.main'].apply(
    lambda x: convert_list_to_string(x))

# Subset of hourly_weather_df for sum of rain
rain_df = hourly_weather_df[['created_date', 'data_rain.1h']]
rain_df = rain_df.resample(TIME_UNIT, on='created_date').sum().reset_index()
rain_df = rain_df.rename({'data_rain.1h': 'data_rain.3h'}, axis=1)

# Calculate the mean of all the values
merged_df = merged_df.resample(
    TIME_UNIT, on='created_date').mean().reset_index()
merged_df = merged_df.merge(
    weather_description_labels_df, on='created_date', how='left')
merged_df = merged_df.merge(
    rain_df, on='created_date', how='left')
merged_df['data_source'].round(0)
merged_df['no_of_clients'].round(2)
del merged_df['id']
del merged_df['data_rain.1h']

filled_data_frame = fill_missing_values_using_forecast(
    merged_df[merged_df['data_main.temp'].isnull()],
    weekly_weather_forecast_df, 'created_date')

merged_df = merged_df.combine_first(filled_data_frame)
merged_df[['data_weather.main', 'data_weather.description', 'day_of_week', 'is_weekend']] = merged_df[['data_weather.main', 'data_weather.description', 'day_of_week', 'is_weekend']].apply(
    lambda x: x.astype('category').cat.codes
)

print(merged_df.head)

print(f"weather main {merged_df['data_weather.main'].unique()}")

print(merged_df.info())

# print('dataframe with null values in temperature')

# print(
#     fill_missing_values_using_forecast(
#         merged_df[merged_df['data_main.temp'].isnull()],
#         weekly_weather_forecast_df,
#         'created_date'))

# print(merged_df.info())
# print('after running function fill_missing_values_using_forecast')
# print(merged_df[merged_df['data_main.temp'].isnull()])

# print(merged_df['day_of_week'].unique())
# print(merged_df[['created_date', 'no_of_clients', 'data_weather.main', 'data_weather.description', 'day_of_week']].head)
# for col in ['data_weather.main', 'data_weather.description', 'day_of_week']:
#     merged_df[[col]] = merged_df[[col]].astype('category')
# print(f"weather main {merged_df['data_weather.main'].unique()}")

# print(merged_df[''])
# print(merged_df.head)
# print(f"type of created_date is {merged_df['data_dt'].dtypes}")
# print(f"columns after resampling are: {list(merged_df)}")
# nan_rows = merged_df[merged_df['data_main.temp'].notnull()]
# print('--------------------')
# print(nan_rows)

# figure = go.Figure()
# figure.add_trace(
#     go.Bar(x=merged_df['created_date'],
#            y=merged_df['no_of_clients'],
#            name="Number of clients"))

# figure.add_trace(
#     go.Scatter(x=merged_df['created_date'],
#                y=merged_df['data_main.temp'],
#                name="Temperature in Celcius"))
# figure.show()
merged_df_dropped_col = merged_df
for item in ['data_source', 'created_date', 'data_main.feels_like', 'random_key']:
    try:
        del merged_df_dropped_col[item]
    except KeyError:
        print(f"key {item} does not exist.")

# print(merged_df_dropped_col.corr())

# merged_df_dropped_col['empty_col'] = ""

# print(merged_df.corr())
# print(merged_df.info())
# hovertext = merged_df.corr().round(4)
# heat = go.Heatmap(
#     z=merged_df.corr(),
#     x=list(merged_df),
#     y=list(merged_df),
#     xgap=1, ygap=1,
#     # colorscale=px.colors.sequential.Plotly3,
#     colorbar_thickness=20,
#     colorbar_ticklen=3,
#     text=merged_df.corr().values,
#     hovertext=hovertext,
#     hoverinfo='text',
# )

hovertext = merged_df_dropped_col.corr().round(4)
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

# test_df = merged_df.groupby(merged_df['created_date'].map(lambda t: t.hour))
# test_df = merged_df.groupby(merged_df['created_date'].to_period('S'))
# print(test_df)

# layout = go.Layout(
#     xaxis_showgrid=False,
#     yaxis_showgrid=False)
# #     yaxis_autorange='reversed')
# figure_2 = go.Figure(data=[heat], layout=layout)
# figure_2.show()

# print(merged_df[['no_of_clients', 'day_of_week']].corr())
# print(merged_df.corr())

# corr = merged_df.corr()
# corr.style.background_gradient(cmap='coolwarm').set_precision(2)
# corr.show()

# temp = merged_df_dropped_col.mask(np.tril(np.ones(merged_df_dropped_col.shape)).astype(np.bool))

figure_3 = ff.create_annotated_heatmap(
    merged_df_dropped_col.corr().values,
    x=list(merged_df_dropped_col), y=list(merged_df_dropped_col),
    annotation_text=merged_df_dropped_col.corr().values.round(4))

figure_3.show()
