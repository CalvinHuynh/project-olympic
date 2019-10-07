from peewee import CharField, DateTimeField, PrimaryKeyField
from playhouse.mysql_ext import JSONField

from .base import Base

class Weather(Base):
    id = PrimaryKeyField()
    created_date = DateTimeField()
    data = JSONField()
