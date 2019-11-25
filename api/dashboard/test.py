import os as _os
from enum import Enum

from dotenv import load_dotenv as _load_dotenv
from pandas import DataFrame, Series
from pandas.io.json import json_normalize
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, MySQLDatabase, PrimaryKeyField)
from playhouse.mysql_ext import JSONField
from playhouse.shortcuts import model_to_dict

import plotly.graph_objects as go
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


data_source_query = DataSourceData.select().where(
    DataSourceData.data_source_id == 2)
# print(query.dicts())
data_source_df = DataFrame(list(data_source_query.dicts()))
# print(data_source_df)

weekly_weather_query = Weather.select().where(
    Weather.weather_forecast_type == Forecast.FIVE_DAYS_THREE_HOUR)

weekly_filter = "{\"5_days_3_hour_forecast\": list[].{dt: dt, main: main,"\
    "weather: {main: weather[0].main, description: weather[0].description },"\
    "clouds: clouds, wind: wind, rain: rain}}"

weekly_weather_array = []
for weather in weekly_weather_query:
    weekly_weather_array.append(model_to_dict(weather, recurse=False))

weekly_weather_df = DataFrame(weekly_weather_array)
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
df = weekly_weather_df.iloc[[0]]
print(list(weekly_weather_df))
# print(type(df))
# print('headers are')
# print(list(df))
# print('types are')
# print(df.dtypes)
# print(df)
flatest_df = flatten_json_data_in_column(weekly_weather_df, 'data', 40)
# print(flatest_df)
# print(list(flatest_df))
# print(weekly_weather_df)
# print('after weekly flatten')
# print(weekly_weather_df.iloc[0])


hourly_weather_query = Weather.select().where(
    Weather.weather_forecast_type == Forecast.HOURLY)
hourly_filter = "{dt: dt,  weather: {main: weather[*].main,"\
    "description: weather[*].description}, main: main, wind: wind"\
    ", rain: rain, clouds: clouds}"

hourly_weather_array = []
for weather in hourly_weather_query:
    hourly_weather_array.append(model_to_dict(weather, recurse=False))

hourly_weater_df = DataFrame(hourly_weather_array)
# print('before hourly filter')
# print(hourly_weater_df.iloc[0])
hourly_weater_df = filter_column_json_data(hourly_weater_df, 'data',
                                           hourly_filter)
# print('after hourly filter')
# print(hourly_weater_df.iloc[0])
hourly_weater_df = flatten_json_data_in_column(hourly_weater_df, 'data')
print('after hourly flatten')
print(hourly_weater_df.iloc[0])

print(hourly_weater_df[['created_date', 'data_main.temp']])
# TODO: create a graph for thesis
figure = go.Figure()
figure.add_trace(
    go.scatter(
        x=hourly_weater_df[['created_date']],
        y=hourly_weater_df[['data_main.temp']]
    )
)

figure.show()
