from peewee import ModelBase
from app import mysql_db

class BaseModel(ModelBase):
    class Meta():
        database = mysql_db