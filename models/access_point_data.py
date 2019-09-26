from peewee import (DateTimeField, ForeignKeyField, IntegerField,
                    PrimaryKeyField)

from .access_point import User
from .base import Base


class AccessPointData(Base):
    id = PrimaryKeyField()
    # Identifies which access point the data belongs to
    access_point = ForeignKeyField(User, related_name='send_by')
    no_of_clients = IntegerField()
    creation_date = DateTimeField()
