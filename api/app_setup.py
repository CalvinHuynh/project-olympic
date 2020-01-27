from datetime import timedelta
from http import HTTPStatus

from authlib.flask.client import OAuth
from flask import Flask, render_template
from flask_jwt_extended import JWTManager

from api.dashboard.dash_overview import add_dash as dash_overview
from api.dashboard.dash_routes import blueprint as dash_blueprint
from api.models import initialize_database
from api.routes import blueprint_api as api_v1
from api.routes import blueprint_index as index
from api.settings import (FLASK_APP_NAME, FLASK_PERMANENT_SESSION_LIFETIME,
                          FLASK_SECRET_KEY, GET_PATH, GITHUB_CLIENT_ID,
                          GITHUB_CLIENT_SECRET, GOOGLE_CLIENT_ID,
                          GOOGLE_CLIENT_SECRET, JWT_ACCESS_TOKEN_EXPIRES,
                          JWT_SECRET_KEY, JWT_TOKEN_LOCATION)

jwt = None
oauth = None


def register_config(app: Flask):
    jwt_locations = []
    for location in JWT_TOKEN_LOCATION:
        jwt_locations.append(location)

    app.config['RESTPLUS_VALIDATE'] = True
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
        seconds=FLASK_PERMANENT_SESSION_LIFETIME)
    app.config['JWT_TOKEN_LOCATION'] = jwt_locations
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
    app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET
    app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
    app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET
    app.config['PROPAGATE_EXCEPTIONS'] = True

    return app


def register_extensions(app: Flask):
    # Initializes oauth
    global oauth
    oauth = OAuth(app)
    # Initializes JWT
    global jwt
    jwt = JWTManager(app)

    return app


def register_errorpages(app: Flask):
    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def page_not_found(e):
        return render_template('error_pages/404.html',
                               msg=e.description), HTTPStatus.NOT_FOUND

    # 401 errors are not being intercepted
    @app.errorhandler(HTTPStatus.UNAUTHORIZED)
    def unauthorized(e):
        return render_template('error_pages/401.html',
                               msg=e.description), HTTPStatus.UNAUTHORIZED

    return app


def register_blueprints(app: Flask):
    app.register_blueprint(index)
    app.register_blueprint(api_v1)
    app.register_blueprint(dash_blueprint)

    return app


def create_app():
    app = Flask(FLASK_APP_NAME if FLASK_APP_NAME else __name__,
                static_url_path='',
                static_folder=GET_PATH() + '/static')
    initialize_database()
    app = register_config(app)
    app = register_extensions(app)
    app = register_errorpages(app)
    # Initializes the routes
    app = register_blueprints(app)
    # Initializes the dash graphs
    app = dash_overview(app)

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
        if 'CSRF' in self:
            return ErrorObject.create_response(self, HTTPStatus.BAD_REQUEST,
                                               'CSRF token missing')
        else:
            return ErrorObject.create_response(self, HTTPStatus.UNAUTHORIZED,
                                               'Access token missing')

    return app
