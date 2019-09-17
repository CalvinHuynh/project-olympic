from peewee import ForeignKeyField
from .base import Base
from .user import User
from .access_point import AccessPoint


class AccessPointToken(Base):
    user = ForeignKeyField(User)
    AccessPoint = ForeignKeyField(AccessPoint)