# For future roles and permission system
from peewee import CharField, PrimaryKeyField, ForeignKeyField

from .base import Base
from .user import User


class Role(Base):
    id = PrimaryKeyField()
    role_name = CharField(unique=True, null=False)
    added_by = ForeignKeyField(User, related_name='added_by')
    # permissions = ForeignKeyField
