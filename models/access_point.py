from peewee import PrimaryKeyField, CharField, ForeignKeyField
from .base import Base
from .user import User


class AccessPoint(Base):
    id = PrimaryKeyField()
    description = CharField()
    user = ForeignKeyField(User, related_name='added_by')