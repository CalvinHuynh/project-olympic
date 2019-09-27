from peewee import CharField, DateTimeField, PrimaryKeyField

from .base import Base


class User(Base):
    id = PrimaryKeyField()
    username = CharField(unique=True)
    email = CharField(unique=True, null=False)
    join_date = DateTimeField()
    last_login_date = DateTimeField()
