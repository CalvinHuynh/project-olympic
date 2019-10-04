import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def GET_PATH():
    return os.path.dirname(os.path.abspath(__file__))

FLASK_APP_NAME = os.getenv("FLASK_APP_NAME")
FLASK_ENV = os.getenv("FLASK_ENV")
FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST")
FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT")
FLASK_API_VERSION = os.getenv("FLASK_API_VERSION")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

SWAGGER_DOC_ENDPOINT = os.getenv("SWAGGER_DOC_ENDPOINT")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
