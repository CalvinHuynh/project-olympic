from peewee import BooleanField, DateTimeField, ForeignKeyField, IntegerField

from .user import User
from .base import Base
from .access_point import AccessPoint


class AccessPointToken(Base):
    user = ForeignKeyField(User)
    access_point = ForeignKeyField(AccessPoint)
    created_date = DateTimeField()
    last_activity_date = DateTimeField(null=True)
    expiry_date = DateTimeField()
    no_of_usage = IntegerField()
    is_active = BooleanField(default=True)
    deactivated_since = DateTimeField()
