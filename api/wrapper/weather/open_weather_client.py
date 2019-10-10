from requests import Session

# For more endpoints, please refer to https://openweathermap.org/api


class OpenWeatherClient():
    def __init__(self, api_key: str, city: str, country_code: str, units: str = 'metric', schema: str = 'http'):
        """Initializes open weather api client
        
        Arguments:
            api_key {str} -- API key
            city {str} -- Name of city
            country_code {str} -- ISO 3166 country code
        
        Keyword Arguments:
            units {str} -- [description] (default: {'metric'})
            schema {str} -- [description] (default: {'http'})
        """
        self.schema = schema
        self.api_key = api_key
        self.city = city
        self.country = country_code
        self.units = units
        self.session = Session()

    def _send_get(self, url):
        result = self.session.get(url)
        return result.text

    def __base_url(self):
        return self.schema + '://' + 'api.openweathermap.org/data/2.5/'

    def get_current_weather(self):
        """Returns a json object with the current weather"""
        try:
            return self._send_get(self.__base_url() + 'weather' + '?q=' + self.city + ',' + self.country +
                                  '&appid=' + self.api_key + '&units=' + self.units)
        except:
            raise

    def get_weather_forecast_5d_3h(self):
        """Returns a 5 day weather forecast"""
        try:
            return self._send_get(self.__base_url() + 'forecast' + '?q=' + self.city + ',' + self.country +
                                  '&appid=' + self.api_key + '&units=' + self.units)
        except:
            raise
