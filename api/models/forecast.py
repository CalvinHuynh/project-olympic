from peewee import CharField, PrimaryKeyField, DateTimeField
from playhouse.mysql_ext import JSONField

from .base import Base


class CrowdForecast(Base):
    id = PrimaryKeyField(),
    created_date = DateTimeField()
    date_range_used = CharField(max_length=50)
    number_of_weeks_used = CharField(max_length=4)
    prediction_for_week_nr = CharField(max_length=2)
    prediction_start_date = CharField(max_length=20)
    prediction_end_date = CharField(max_length=20)
    prediction_data = JSONField()

    class Meta:
        indexes = (
            ((
                'date_range_used',
                'prediction_start_date',
                'prediction_end_date'
            ), True),
        )
