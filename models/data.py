from peewee import *
from models.base_model import BaseModel
from models.access_point import AccessPoint


class AccessPointData(BaseModel):
    id = PrimaryKeyField()
    access_point = ForeignKeyField(AccessPoint, related_name='send_by')
    no_of_clients = IntegerField()
    creation_date = DateTimeField()
