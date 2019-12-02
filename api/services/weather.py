import json
from http import HTTPStatus

from playhouse.shortcuts import model_to_dict

from api.helpers import to_utc_datetime, filter_items_from_list
from api.models import Weather, Forecast
from api.settings import OPEN_WEATHER_API_KEY
from api.wrapper import OpenWeatherClient

_ALLOWED_SORT_VALUES = ['asc', 'desc']
_client = OpenWeatherClient(OPEN_WEATHER_API_KEY, 'Amsterdam', 'NL')


class WeatherService():
    def get_current_weather(self):
        """Retrieves the current weather data"""
        weather_data = _client.get_current_weather()
        try:
            Weather.create(created_date=to_utc_datetime(),
                           data=weather_data,
                           data_source=1,
                           weather_forecast_type=Forecast.HOURLY)
            return HTTPStatus.CREATED
        except BaseException:
            raise

    def get_weather_forecast_5d_3h(self):
        """Retrieves the 5 days 3 hour weather forecast"""
        weather_data = _client.get_weather_forecast_5d_3h()
        try:
            Weather.create(created_date=to_utc_datetime(),
                           data=weather_data,
                           data_source=1,
                           weather_forecast_type=Forecast.FIVE_DAYS_THREE_HOUR)
            return HTTPStatus.CREATED
        except BaseException:
            raise

    # flake8: noqa: C901
    def retrieve_all_weather_data(self, limit: int, start_date: str,
                                  end_date: str, order_by: str, sort: str,
                                  forecast_type: str):
        """Retrieves all weather data

        Arguments:
            limit {int} -- limits the number of results
            start_date {str} -- start date
            end_date {str} -- end date
            order_by {str} -- order result by given key
            sort {str} -- sorts the data in ascending or descending order
            forecast_type {str} -- forecast type

        Returns:
            WeatherData -- An array of all weather data
        """
        all_data_array = []

        obj_attributes = filter_items_from_list(dir(Weather), '^__')
        order_by_field = Weather

        query = Weather.select()

        # Set defaults
        if not limit:
            limit = 20
        if not order_by:
            order_by = 'id'
        if not sort:
            sort = 'desc'

        if start_date:
            query = query.where(Weather.created_date >= start_date)
        if end_date:
            query = query.where(Weather.created_date <= end_date)

        if order_by.strip().lower() in obj_attributes:
            order_by_field = getattr(Weather, order_by.strip().lower())
        else:
            raise ValueError(HTTPStatus.BAD_REQUEST,
                             f'Field {order_by.strip().lower()} does not exist')

        if sort.lower() in _ALLOWED_SORT_VALUES:
            if sort.lower() == _ALLOWED_SORT_VALUES[0]:
                query = query.order_by(order_by_field.asc())
            else:
                query = query.order_by(order_by_field.desc())
        else:
            raise ValueError(
                HTTPStatus.BAD_REQUEST,
                'Invalid sort value, only "asc" or "desc" are allowed')

        try:
            casted_limit = int(limit)
        except ValueError:
            raise ValueError(
                HTTPStatus.BAD_REQUEST,
                'Invalid limit value, only values of type <int> are allowed')

        query = query.limit(casted_limit)

        if forecast_type == 'hourly':
            query = query.where(Weather.weather_forecast_type == 'HOURLY')
        elif forecast_type == 'weekly':
            query = query.where(
                Weather.weather_forecast_type == 'FIVE_DAYS_THREE_HOUR')

        try:
            for result in query:
                result.data = json.loads(result.data)  # escapes json data
                all_data_array.append(model_to_dict(result, recurse=False))
            return all_data_array
        except BaseException:
            raise
