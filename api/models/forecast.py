from peewee import CharField, PrimaryKeyField, DateTimeField
from playhouse.mysql_ext import JSONField

from .base import Base


class CrowdForecast(Base):
    id = PrimaryKeyField(),
    created_date = DateTimeField()
    date_range_used = CharField(unique=True, max_length=50)
    prediction_for_week = CharField(max_length=2)
    prediction_start_date = CharField(max_length=20)
    prediction_data = JSONField()
