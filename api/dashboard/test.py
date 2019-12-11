import os as _os
from datetime import datetime as dt
from enum import Enum

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dotenv import load_dotenv as _load_dotenv
from pandas import DataFrame, Series, to_datetime
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
    all_columns_in_df = list(df)
    for col in all_columns_in_df:
        if col.endswith(postfix_to_drop):
            del df[col]
    return df


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

hourly_weater_df = DataFrame(hourly_weather_array)

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

# # print('before weekly filter')
# # print(weekly_weather_df.iloc[0])
# weekly_weather_df = filter_column_json_data(weekly_weather_df, 'data',
#                                             weekly_filter)
# # print('after weekly filter')
# # print(weekly_weather_df.iloc[0])
# weekly_weather_df = flatten_json_data_in_column(weekly_weather_df, 'data')
# # print(weekly_weather_df)
# # weekly_weather_df.pipe(
# #     lambda x: x.drop('data.5_days_3_hour_forecast', 1).join(
# #         x['data.5_days_3_hour_forecast'].apply(lambda y: Series(merge(y)))
# #     )
# # )

# # print('before splitting data_5_days_3_hour_forecast')
# # print(weekly_weather_df)

# # Flattens the json array that resides in the specified column and removes it
# # after it is done

# # weekly_weather_df = weekly_weather_df['data_5_days_3_hour_forecast'].apply(
# #     Series).merge(weekly_weather_df, left_index=True,
# #                   right_index=True).drop(['data_5_days_3_hour_forecast'],
# #                                          axis=1)

# weekly_weather_df = unpack_json_array(weekly_weather_df,
#                                       'data_5_days_3_hour_forecast')

# # print('after splitting data_5_days_3_hour_forecast')
# # print(weekly_weather_df)
# # weekly_weather_df = weekly_weather_df.rename(columns=_rename_column)
# weekly_weather_df.columns = map(_rename_columns, weekly_weather_df.columns)
# df = weekly_weather_df.iloc[[0]]
# # print(list(weekly_weather_df))
flatest_df = flatten_json_data_in_column(weekly_weather_df, 'data', 40)

hourly_filter = "{dt: dt,  weather: {main: weather[*].main,"\
    "description: weather[*].description}, main: main, wind: wind"\
    ", rain: rain, clouds: clouds}"

# print('before hourly filter')
# print(hourly_weater_df.iloc[0])
hourly_weater_df = filter_column_json_data(hourly_weater_df, 'data',
                                           hourly_filter)
# print('after hourly filter')
# print(hourly_weater_df.iloc[0])
hourly_weater_df = flatten_json_data_in_column(hourly_weater_df, 'data')
# hourly_weater_df["created_date"] = hourly_weater_df["created_date"].round("S")
hourly_weater_df['created_date'] = hourly_weater_df['created_date'].map(
    lambda x: x.replace(second=0))
# print('after hourly flatten')
# print(hourly_weater_df.iloc[0])
# print(hourly_weater_df.loc[[hourly_weater_df['id'] == 5674], ['id', 'created_date', 'data_main.temp']])
print('------------------ print where id is 5674')
print(hourly_weater_df.query("id == 5674")[
      ['id', 'created_date', 'data_main.temp']])
print(hourly_weater_df[['created_date', 'data_main.temp']])

merged_df = data_source_df.merge(
    hourly_weater_df, on='created_date', how='left')
print(list(merged_df))
# Clean dataframe
merged_df = drop_columns_with_postfix(merged_df)
merged_df.rename(
    columns={'id_x': 'id', 'data_source_x': 'data_source'}, inplace=True)

print(merged_df)
print(merged_df.tail(n=10))
print(f"columns before resampling are: {list(merged_df)}")
print(merged_df.info())
merged_df.created_date = to_datetime(merged_df.created_date, unit='s')
merged_df = merged_df.resample('H', on='created_date', ).mean().reset_index()
merged_df['day_of_week'] = merged_df['created_date'].dt.day_name()
# print(merged_df.info())
merged_df.data_source.round(0)
del merged_df['id']
print(merged_df)
print(f"type of created_date is {merged_df['data_dt'].dtypes}")
print(f"columns after resampling are: {list(merged_df)}")
# nan_rows = merged_df[merged_df['data_main.temp'].notnull()]
# print('--------------------')
# print(nan_rows)
figure = go.Figure()
figure.add_trace(
    go.Bar(x=merged_df['created_date'],
           y=merged_df['no_of_clients'],
           name="Number of clients"))

figure.add_trace(
    go.Scatter(x=merged_df['created_date'],
               y=merged_df['data_main.temp'],
               name="Temperature in Celcius"))
# figure.show()
hovertext = merged_df.corr().round(2)
heat = go.Heatmap(
    z=merged_df.corr(),
    x=list(merged_df),
    y=list(merged_df),
    xgap=1, ygap=1,
    colorscale=px.colors.sequential.Viridis,
    colorbar_thickness=20,
    colorbar_ticklen=3,
    text=merged_df.corr(),
    hovertext=hovertext,
    hoverinfo='text',
)

# test_df = merged_df.groupby(merged_df['created_date'].map(lambda t: t.hour))
# test_df = merged_df.groupby(merged_df['created_date'].to_period('T'))
# print(test_df)

# layout = go.Layout(
#     xaxis_showgrid=False,
#     yaxis_showgrid=False)
# #     yaxis_autorange='reversed')
# figure_2 = go.Figure(data=[heat], layout=layout)
# figure_2.show()

# corr = merged_df.corr()
# corr.style.background_gradient(cmap='coolwarm').set_precision(2)
# corr.show()

# figure_3 = ff.create_annotated_heatmap(
#     merged_df.corr(), zmin=0)

# figure_3.show()
