import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_restplus import Api, Resource, fields

from models import initialize_database
from routes import api

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

initialize_database()
# TODO: Compare the pros and cons of a dot env file versus configuration file
# app.config.from_object('config.Configuration')

app = Flask(
    os.getenv("FLASK_APP_NAME").strip() if os.getenv("FLASK_APP_NAME").strip(
    ) else __name__)

# Initializes the routes
api.init_app(app)
