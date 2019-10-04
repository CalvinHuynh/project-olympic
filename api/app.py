from http import HTTPStatus
from authlib.flask.client import OAuth
from flask import Flask
from flask_jwt_extended import JWTManager

from api.models import initialize_database
from api.routes import blueprint_index as index
from api.routes import blueprint as api_v1

from api.settings import (FLASK_APP_NAME, FLASK_SECRET_KEY,GITHUB_CLIENT_ID,
                      GITHUB_CLIENT_SECRET, GOOGLE_CLIENT_ID,
                      GOOGLE_CLIENT_SECRET, JWT_SECRET_KEY)

initialize_database()

app = Flask(FLASK_APP_NAME if FLASK_APP_NAME else __name__)

app.config['RESTPLUS_VALIDATE'] = True
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET
app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET

# Initializes oauth
oauth = OAuth(app)

# Initializes JWT
jwt = JWTManager(app)

# Overwrite default error handling
@jwt.invalid_token_loader
def custom_invalid_token_loader(self):
    from api.helpers import ErrorObject
    return ErrorObject.create_response(self, HTTPStatus.UNAUTHORIZED,
                                        'Invalid token provided')

@jwt.expired_token_loader
def custom_expired_token_loader(callback):
    from api.helpers import ErrorObject
    token_type = callback['type']
    return ErrorObject.create_response(
        ErrorObject, HTTPStatus.UNAUTHORIZED,
        'The {} token has expired'.format(token_type))

@jwt.unauthorized_loader
def custom_unauthorized_loader(self):
    from api.helpers import ErrorObject
    return ErrorObject.create_response(self, HTTPStatus.UNAUTHORIZED,
                                        'No access token provided')


# Initializes the routes
app.register_blueprint(index)
app.register_blueprint(api_v1)

if __name__ == "__main__":
    app.run()
