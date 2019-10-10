from enum import Enum
from peewee import CharField, DateTimeField, PrimaryKeyField, ForeignKeyField
from playhouse.mysql_ext import JSONField

from .data_source import DataSource
from .base import Base


class Weather(Base):
    id = PrimaryKeyField()
    created_date = DateTimeField()
    data = JSONField()
    data_source = ForeignKeyField(DataSource, related_name='send_by')
    weather_forecast_type = CharField()


class Forecast(Enum):
    """The 2 types of forecasts that are currently available for the free tier API of Openweathermap."""
    # Return the name instead of the value, as the name gives more information
    def __str__(self):
        return str(self.name)
    HOURLY = 1
    FIVE_DAYS_THREE_HOUR = 2
