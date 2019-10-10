import json
from datetime import datetime
from http import HTTPStatus

from playhouse.shortcuts import model_to_dict

from api.helpers import to_utc_datetime
from api.models import Weather, Forecast
from api.settings import OPEN_WEATHER_API_KEY
from api.wrapper import OpenWeatherClient

_client = OpenWeatherClient(OPEN_WEATHER_API_KEY, 'Amsterdam', 'NL')


class WeatherService():

    def get_current_weather(self):
        """Retrieves the current weather data"""
        weather_data = _client.get_current_weather()
        try:
            Weather.create(
                created_date=to_utc_datetime(),
                data=weather_data,
                data_source=1,
                weather_forecast_type=Forecast.HOURLY)
            return HTTPStatus.CREATED
        except:
            raise

    def get_weather_forecast_5d_3h(self):
        """Retrieves the 5 days 3 hour weather forecast"""
        weather_data = _client.get_weather_forecast_5d_3h()
        try:
            Weather.create(
                created_date=to_utc_datetime(),
                data=weather_data,
                data_source=1,
                weather_forecast_type=Forecast.FIVE_DAYS_THREE_HOUR)
            return HTTPStatus.CREATED
        except:
            raise

    def retrieve_all_weather_data(self):
        """Retrieves all weather data
        
        Returns:
            WeatherData -- An array of all weather data
        """
        all_data_array = []
        try:
            for result in Weather.select():
                result.data = json.loads(result.data)  # escapes json data
                all_data_array.append(model_to_dict(result))
            return all_data_array
        except:
            raise
