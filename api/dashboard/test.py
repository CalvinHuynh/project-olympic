import os as _os
from enum import Enum
from json import dumps, loads

from dotenv import load_dotenv as _load_dotenv
from jmespath import search
from pandas import DataFrame
from pandas.io.json import json_normalize
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, MySQLDatabase, PrimaryKeyField)
from playhouse.mysql_ext import JSONField
from playhouse.shortcuts import dict_to_model, model_to_dict

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


# # database.connection()
data_source_query = DataSourceData.select().where(
    DataSourceData.data_source_id == 2)
# print(query.dicts())
data_source_df = DataFrame(list(data_source_query.dicts()))
# print(data_source_df)

# weather_forecast_weekly_query = Weather.select().where(
#     Weather.weather_forecast_type == Forecast.FIVE_DAYS_THREE_HOUR)
# weather_forecast_df = DataFrame(list(weather_forecast_weekly_query.dicts()))
# print(weather_forecast_df)

# weekly_filter = "{\"5_days_3_hour_forecast\": list[].{dt: dt, main: main,"\
#     "weather: {description: [weather[*].description]}, clouds: clouds,"\
#     "wind: wind, rain: rain}}"
# print("filtered weekly")
# print(search(weekly_filter, loads(weather_forecast_df.iloc[1]['data'])))

weather_hourly_query = Weather.select().where(
    Weather.weather_forecast_type == Forecast.HOURLY)
hourly_filter = "{dt: dt, weather_description: weather[0].description, main: main, wind: wind, rain: rain, clouds: clouds}"

# all_weather = list(weather_hourly_query)
# print(f'length is {len(all_weather)}')

all_weather_array = []
for weather in weather_hourly_query:
    all_weather_array.append(model_to_dict(weather, recurse=False))

# testing_df = DataFrame(all_weather_array)
testing_df_1 = DataFrame(all_weather_array)

for i in range(len(testing_df_1)):
    testing_df_1['data'].values[i] = search(
        hourly_filter, loads(testing_df_1['data'].values[i]))

testing_df_2 = json_normalize(testing_df_1)

# TODO: flatten json and create a graph for thesis

## flatten json
# testing_df_2 = testing_df_1.join(
#     json_normalize(
#         testing_df_1['data'].map(loads).tolist()).add_prefix('data.')).drop(
#             ['data'], axis=1)

# print(testing_df_2)

# weather_hourly_df = DataFrame(list(weather_hourly_query.dicts()))

# print(weather_hourly_df)
# print(weather_hourly_df.iloc[3170]['data'])
# print("filtered hourly")
# filtered_result = search(hourly_filter,
#                          loads(weather_hourly_df.iloc[3170]['data']))
# print(dumps(filtered_result))
# print(json_normalize(filtered_result))
