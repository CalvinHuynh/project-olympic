import os as _os
from pathlib import Path as _Path

from dotenv import load_dotenv as _load_dotenv

env_path = _Path('.') / '.env'
_load_dotenv(dotenv_path=env_path)


def GET_PATH():
    """Retrieves the current directory"""
    return _os.path.dirname(_os.path.abspath(__file__))


def _split_string(input_to_split: str, delimiter: str = ','):
    """Split a given input string by given delimiter

    Arguments:
        input_to_split {str} -- String to split

    Keyword Arguments:
        delimiter {str} -- Delimiter to use (default: {','})

    Returns:
        {list} -- List of splitted strings
    """
    splitted_string = input_to_split.lower().replace(' ', '').split(delimiter)
    return splitted_string


FLASK_APP_NAME = _os.getenv("FLASK_APP_NAME")
FLASK_ENV = _os.getenv("FLASK_ENV")
FLASK_RUN_HOST = _os.getenv("FLASK_RUN_HOST")
FLASK_RUN_PORT = _os.getenv("FLASK_RUN_PORT")
FLASK_API_VERSION = _os.getenv("FLASK_API_VERSION")
FLASK_SECRET_KEY = _os.getenv("FLASK_SECRET_KEY")

NUMBER_OF_BACKGROUND_WORKERS = _os.getenv("NUMBER_OF_BACKGROUND_WORKERS")

JWT_SECRET_KEY = _os.getenv("JWT_SECRET_KEY")
JWT_TOKEN_LOCATION = _split_string(_os.getenv("JWT_TOKEN_LOCATION"))
JWT_ACCESS_TOKEN_EXPIRES = int(_os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
FLASK_PERMANENT_SESSION_LIFETIME = JWT_ACCESS_TOKEN_EXPIRES

SWAGGER_DOC_ENDPOINT = _os.getenv("SWAGGER_DOC_ENDPOINT")

ALLOWED_OAUTH_CLIENTS = _split_string(_os.getenv('ALLOWED_OAUTH_CLIENTS'))

GITHUB_CLIENT_ID = _os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = _os.getenv("GITHUB_CLIENT_SECRET")

GOOGLE_CLIENT_ID = _os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _os.getenv("GOOGLE_CLIENT_SECRET")

MYSQL_HOST = _os.getenv("MYSQL_HOST")
MYSQL_DATABASE = _os.getenv("MYSQL_DATABASE")
MYSQL_USER = _os.getenv("MYSQL_USER")
MYSQL_PASSWORD = _os.getenv("MYSQL_PASSWORD")

UNIFI_ADDRESS = _os.getenv("UNIFI_ADDRESS")
UNIFI_USER = _os.getenv("UNIFI_USER")
UNIFI_PASSWORD = _os.getenv("UNIFI_PASSWORD")

OPEN_WEATHER_API_KEY = _os.getenv("OPEN_WEATHER_API_KEY")
