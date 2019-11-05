from .data_source import DataSource
from .data_source_data import DataSourceData
from .data_source_token import DataSourceToken
from .base import Base, MySQLDatabase, database
from .user import User
from .weather import Weather, Forecast


def create_tables(database: MySQLDatabase, migrations: bool = False):
    """Creates database tables
    
    Arguments:
        database {MySQLDatabase} -- MySQL database connection
    
    Keyword Arguments:
        migrations {bool} -- Run migrations (in this case only a rename of \
            a column is run) (default: {False})
    
    Raises:
        ValueError: Provide a MySQLDatabase class
    """
    if isinstance(database, MySQLDatabase):
        with database:
            database.create_tables(Base.__subclasses__(), safe=True)
            if migrations:
                from playhouse.migrate import MySQLMigrator, migrate
                migrator = MySQLMigrator(database)
                try:
                    migrate(
                        migrator.rename_column('data_source_data',
                                               'creation_date',
                                               'created_date'))
                except:
                    pass
    else:
        raise ValueError(
            "Please provide a database class that is an instance of \
                MySQLDatabase")


def _seed():
    """Creates the admin and a data source"""
    from api.helpers import to_utc_datetime
    join_date = to_utc_datetime()
    user = User.get_or_create(email='calvin.huynh@incentro.com',
                              defaults={
                                  'join_date': join_date,
                                  'last_login_date': join_date,
                                  'username': 'admin'
                              })

    DataSource.get_or_create(
        id=1,
        defaults={
            'source': 'system_scheduled_task',
            'description':
            'A data source that is used to send the result from the scheduled \
                task',
            'user': user[0].id
        })


def initialize_database():
    create_tables(database, migrations=True)
    _seed()
