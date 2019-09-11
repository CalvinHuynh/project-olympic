from peewee import *
from models.base_model import BaseModel


class User(BaseModel):
    id = PrimaryKeyField()
    username = CharField(unique=True)
    email = CharField()
    join_date = DateTimeField()
    last_login_date = DateTimeField()