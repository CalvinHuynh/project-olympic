from peewee import CharField, PrimaryKeyField, DateTimeField
from playhouse.mysql_ext import JSONField

from .base import Base


class CrowdForecast(Base):
    id = PrimaryKeyField(),
    created_date = DateTimeField()
    prediction_for_date_range = CharField(unique=True, max_length=50)
    prediction_data = JSONField()
