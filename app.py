import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(os.getenv("FLASK_APP_NAME"))
# TODO: Compare the pros and cons of a dot env file versus configuration file
# app.config.from_object('config.Configuration')

from models import init_default
init_default()