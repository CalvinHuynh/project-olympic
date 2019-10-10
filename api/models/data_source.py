from peewee import CharField, ForeignKeyField, PrimaryKeyField

from .base import Base
from .user import User


class DataSource(Base):
    id = PrimaryKeyField()
    source = CharField(unique=True, max_length=25)
    description = CharField()
    user = ForeignKeyField(User, related_name='added_by')
