from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField
from .base import Base
from .access_point import User


class AccessPointData(Base):
    id = PrimaryKeyField()
    # Identifies which access point the data belongs to
    access_point = ForeignKeyField(User, related_name='send_by')
    no_of_clients = IntegerField()
    creation_date = DateTimeField()
