import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

FLASK_APP_NAME = os.getenv("FLASK_APP_NAME")
FLASK_ENV = os.getenv("FLASK_ENV")
FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST")
FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT")
FLASK_API_VERSION = os.getenv("FLASK_API_VERSION")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

SWAGGER_DOC_ENDPOINT = os.getenv("SWAGGER_DOC_ENDPOINT")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
