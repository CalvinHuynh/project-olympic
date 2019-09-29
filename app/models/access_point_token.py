from peewee import ForeignKeyField, DateTimeField, IntegerField

from .access_point import User
from .base import Base
from .user import User


class AccessPointToken(Base):
    user = ForeignKeyField(User)
    access_point = ForeignKeyField(User)
    created_date = DateTimeField()
    last_activity_date = DateTimeField()
    no_of_hits = IntegerField()
