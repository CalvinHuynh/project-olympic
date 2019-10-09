from datetime import datetime
from http import HTTPStatus

from playhouse.shortcuts import model_to_dict

from api.helpers import to_utc_datetime
from api.models import Weather
from api.settings import OPEN_WEATHER_API_KEY
from api.wrapper import OpenWeatherClient

client = OpenWeatherClient(OPEN_WEATHER_API_KEY, 'Amsterdam', 'NL')


class WeatherService():

    def create_current_weather(self):
        """Retrieves the current weather data"""
        weather_data = client.get_current_weather()
        Weather.create(
            created_date=to_utc_datetime(),
            data=weather_data)

    def retrieve_all_weather_data(self):
        """Retrieves all weather data
        
        Returns:
            WeatherData -- An array of all weather data
        """
        all_data_array = []

        for data in Weather.select():
            all_data_array.append(model_to_dict(data))

        return all_data_array
