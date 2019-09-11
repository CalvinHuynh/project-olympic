import os
import peewee as db

from flask import Flask
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
# TODO: Compare the pros and cons of a dot env file versus configuration file
# app.config.from_object('config.Configuration')

mysql_db = db.MySQLDatabase(os.getenv("FLASK_APP_NAME"),
                            user=os.getenv("MYSQL_USER"),
                            password=os.getenv("MYSQL_PASSWORD"),
                            host=os.getenv("MYSQL_HOST").strip()
                            if os.getenv("MYSQL_HOST").strip() else "0.0.0.0",
                            port=3306)

models = db.ModelBase.__bases__


def create_tables():
    with mysql_db:
        mysql_db.create_tables(models)

create_tables()
