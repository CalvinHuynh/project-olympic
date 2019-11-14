from http import HTTPStatus

from authlib.flask.client import OAuth
# from dash import Dash
from flask import Flask
from flask_jwt_extended import JWTManager

from api.models import initialize_database
from api.routes import blueprint_api as api_v1
from api.routes import blueprint_index as index
from api.dashboard.dash_routes import blueprint as dash_blueprint
from api.settings import (FLASK_APP_NAME, FLASK_SECRET_KEY, GET_PATH,
                          GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
                          GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
                          JWT_SECRET_KEY)
from api.dashboard.dash_app_1 import add_dash

jwt = None
oauth = None


# def register_dashapps(app):
#     from api.dashboard.dash_app_1 import layout
#     # from api.dashboard.dash_app_1 import register_callbacks

#     # Meta tags for viewport responsiveness
#     meta_viewport = {
#         "name": "viewport",
#         "content": "width=device-width, initial-scale=1, shrink-to-fit=no"
#     }

#     dashapp1 = Dash(__name__,
#                     server=app,
#                     url_base_pathname='/dashboard/',
#                     meta_tags=[meta_viewport])

#     with app.app_context():
#         dashapp1.title = 'Dashapp 1'
#         dashapp1.layout = layout
#         # register_callbacks(dashapp1)


def register_config(app: Flask):
    app.config['RESTPLUS_VALIDATE'] = True
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
    app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET
    app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
    app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET
    app.config['PROPAGATE_EXCEPTIONS'] = True


def register_extensions(app: Flask):
    # Initializes oauth
    global oauth
    oauth = OAuth(app)
    # Initializes JWT
    global jwt
    jwt = JWTManager(app)


def create_app():
    app = Flask(FLASK_APP_NAME if FLASK_APP_NAME else __name__,
                static_url_path='',
                static_folder=GET_PATH() + '/static')
    initialize_database()
    register_config(app)
    register_extensions(app)
    # register_dashapps(app)
    # Initializes the routes
    app.register_blueprint(index)
    app.register_blueprint(api_v1)
    app.register_blueprint(dash_blueprint)
    app = add_dash(app)

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

    return app
