from peewee import (BooleanField, DateTimeField, ForeignKeyField, IntegerField,
                    PrimaryKeyField)

from .base import Base
from .data_source import DataSource
from .user import User


class DataSourceToken(Base):
    id = PrimaryKeyField()
    user = ForeignKeyField(User)
    data_source = ForeignKeyField(DataSource)
    created_date = DateTimeField()
    last_activity_date = DateTimeField(null=True)
    expiry_date = DateTimeField()
    no_of_usage = IntegerField()
    is_active = BooleanField(default=True)
    deactivated_since = DateTimeField()
