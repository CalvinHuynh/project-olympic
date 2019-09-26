from peewee import ForeignKeyField

from .access_point import User
from .base import Base
from .user import User


class AccessPointToken(Base):
    user = ForeignKeyField(User)
    AccessPoint = ForeignKeyField(User)
