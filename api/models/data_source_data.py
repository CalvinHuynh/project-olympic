from peewee import (DateTimeField, ForeignKeyField, IntegerField,
                    PrimaryKeyField)

from .data_source import DataSource
from .base import Base


class DataSourceData(Base):
    id = PrimaryKeyField()
    # Identifies which access point the data belongs to
    data_source = ForeignKeyField(DataSource, related_name='send_by')
    no_of_clients = IntegerField()
    creation_date = DateTimeField()
