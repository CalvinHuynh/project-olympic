import os as _os
from enum import Enum

from dotenv import load_dotenv as _load_dotenv
from pandas import DataFrame
from pandas.io.json import json_normalize
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, MySQLDatabase, PrimaryKeyField)
from playhouse.mysql_ext import JSONField
from playhouse.shortcuts import model_to_dict

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
                                custom_prefix: str = None):
    """Flattens the json of a specific column of the given dataframe

    Arguments:
        data_frame {DataFrame} -- input dataframe
        column_to_flatten {str} -- column to flatten

    Keyword Arguments:
        custom_prefix {str} -- custom prefix for the flattened output (default: column)

    Returns:
        [type] -- [description]
    """
    prefix = None
    if custom_prefix:
        prefix = custom_prefix
    else:
        prefix = f'{column_to_flatten}.'

    return data_frame.join(
        json_normalize(
            data_frame[column_to_flatten].tolist()).add_prefix(prefix)).drop(
                [column_to_flatten], axis=1)


data_source_query = DataSourceData.select().where(
    DataSourceData.data_source_id == 2)
# print(query.dicts())
data_source_df = DataFrame(list(data_source_query.dicts()))
# print(data_source_df)

weekly_weather_query = Weather.select().where(
    Weather.weather_forecast_type == Forecast.FIVE_DAYS_THREE_HOUR)

weekly_filter = "{\"5_days_3_hour_forecast\": list[].{dt: dt, main: main,"\
    "weather: {description: [weather[*].description]}, clouds: clouds,"\
    "wind: wind, rain: rain}}"

weekly_weather_array = []
for weather in weekly_weather_query:
    weekly_weather_array.append(model_to_dict(weather, recurse=False))

weekly_weather_df = DataFrame(weekly_weather_array)
# print('before')
# print(weekly_weather_df.iloc[0]['data'])
weekly_weather_df = filter_column_json_data(weekly_weather_df, 'data',
                                            weekly_filter)
# print('after')
# print(weekly_weather_df.iloc[0]['data'])
# weekly_weather_df = flatten_json_data_in_column(weekly_filter, 'data') # does not work yet
# print('weekly weather df')
# print(weekly_weather_df)

hourly_weather_query = Weather.select().where(
    Weather.weather_forecast_type == Forecast.HOURLY)
hourly_filter = "{dt: dt, weather_description: weather[0].description,"\
    "main: main, wind: wind, rain: rain, clouds: clouds}"

hourly_weather_array = []
for weather in hourly_weather_query:
    hourly_weather_array.append(model_to_dict(weather, recurse=False))

hourly_weater_df = DataFrame(hourly_weather_array)
# print('before')
# print(hourly_weater_df.iloc[0]['data'])
hourly_weater_df = filter_column_json_data(hourly_weater_df, 'data',
                                           hourly_filter)
# print('after')
# print(hourly_weater_df.iloc[0]['data'])
hourly_weater_df = flatten_json_data_in_column(hourly_weater_df, 'data')
# print('hourly weather df')
# print(hourly_weater_df.iloc[0])

# TODO: create a graph for thesis
