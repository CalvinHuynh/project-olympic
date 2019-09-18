from .base import database, MySQLDatabase, Base
from .user import User
from .access_point import AccessPoint
from .access_point_token import AccessPointToken
from .access_point_data import AccessPointData


def create_tables(database, models):
    if isinstance(database, MySQLDatabase):
        with database:
            database.create_tables(models, safe=True)
    else:
        print(
            "Please provide a database class that is an instance of MySQLDatabase"
        )


def initialize_database():
    create_tables(database, Base.__subclasses__())
