from .data_source import DataSource
from .data_source_data import DataSourceData
from .data_source_token import DataSourceToken
from .base import Base, MySQLDatabase, database
from .user import User
from .weather import Weather, Forecast


def create_tables(database: MySQLDatabase, models):
    if isinstance(database, MySQLDatabase):
        with database:
            database.create_tables(models, safe=True)
    else:
        raise ValueError(
            "Please provide a database class that is an instance of MySQLDatabase"
        )


def _seed():
    """Creates the admin and a data source"""
    from api.helpers import to_utc_datetime
    join_date = to_utc_datetime()
    user = User.get_or_create(email='calvin.huynh@incentro.com', defaults={
        'join_date': join_date,
        'last_login_date': join_date,
        'username': 'admin'
    })

    data_source = DataSource.get_or_create(id=1, defaults={
        'source': 'system_scheduled_task',
        'description': 'A data source that is used to send the result from the scheduled task',
        'user': user[0].id
    })


def initialize_database():
    create_tables(database, Base.__subclasses__())
    _seed()
