from http import HTTPStatus
from authlib.flask.client import OAuth
from flask import Flask
from flask_jwt_extended import JWTManager

from app.models import initialize_database
from app.routes import blueprint_index as index
from app.routes import blueprint as api_v1

from settings import (FLASK_APP_NAME, FLASK_SECRET_KEY,GITHUB_CLIENT_ID,
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


# @jwt.expired_token_loader
# def custom_expired_token_loader(self, token):
#     from app.helpers import ErrorObject
#     token_type = token['type']
#     return ErrorObject.create_response(
#         self, HTTPStatus.UNAUTHORIZED,
#         'The {} token has expired'.format(token_type))

# @jwt.unauthorized_loader
# def custom_unauthorized_loader(self):
#     from app.helpers import ErrorObject
#     return ErrorObject.create_response(self, HTTPStatus.UNAUTHORIZED,
#                                         'No access token provided')


# Initializes the routes
# api.init_app(app)
app.register_blueprint(index)
app.register_blueprint(api_v1)

if __name__ == "__main__":
    app.run()
