from peewee import CharField, DateTimeField, PrimaryKeyField, ForeignKeyField
from playhouse.mysql_ext import JSONField

from .data_source import DataSource
from .base import Base

class Weather(Base):
    id = PrimaryKeyField()
    created_date = DateTimeField()
    data = JSONField()
    data_source = ForeignKeyField(DataSource, related_name='send_by')
