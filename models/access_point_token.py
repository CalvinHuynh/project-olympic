from peewee import *
from models.base_model import BaseModel
from models.user import User
from models.access_point import AccessPoint


class AccessPointToken(BaseModel):
    user = ForeignKeyField(User)
    AccessPoint = ForeignKeyField(AccessPoint)