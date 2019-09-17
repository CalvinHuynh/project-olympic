import os
from pathlib import Path

from dotenv import load_dotenv
from peewee import Model, MySQLDatabase

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

database = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
                         user=os.getenv("MYSQL_USER"),
                         password=os.getenv("MYSQL_PASSWORD"),
                         host=os.getenv("MYSQL_HOST").strip()
                         if os.getenv("MYSQL_HOST").strip() else "127.0.0.1",
                         port=3306)


class Base(Model):
    class Meta:
        database = database
        legacy_table_names = False
