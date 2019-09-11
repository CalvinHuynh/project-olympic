from peewee import *
from models.base_model import BaseModel
from models.user import User


class AccessPoint(BaseModel):
    id = PrimaryKeyField()
    description = CharField()
    user = ForeignKeyField(User, related_name='added_by')