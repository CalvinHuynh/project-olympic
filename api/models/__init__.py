from .access_point import AccessPoint
from .access_point_data import AccessPointData
from .access_point_token import AccessPointToken
from .base import Base, MySQLDatabase, database
from .user import User
from .weather import Weather


def create_tables(database: MySQLDatabase, models):
    if isinstance(database, MySQLDatabase):
        with database:
            database.create_tables(models, safe=True)
    else:
        raise ValueError(
            "Please provide a database class that is an instance of MySQLDatabase"
        )


def initialize_database():
    create_tables(database, Base.__subclasses__())
