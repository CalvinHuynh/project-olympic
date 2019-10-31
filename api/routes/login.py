import sys

from flask import (Response, make_response, redirect, render_template)
from flask_jwt_extended import create_access_token
from flask_restplus import Namespace, Resource
from loginpass import __all__ as _LOGINPASS_OAUTH_BACKENDS
from playhouse.shortcuts import dict_to_model, model_to_dict

from api.helpers import ErrorObject, to_utc_datetime
from api.models import User
from api.services import UserService
from api.settings import (ALLOWED_OAUTH_CLIENTS as _ALLOWED_OAUTH_CLIENTS,
                          FLASK_APP_NAME as _FLASK_APP_NAME)

api = Namespace('auth', description="Auth related operations")
_CLIENTS = [
    i for i in _LOGINPASS_OAUTH_BACKENDS if i.lower() in _ALLOWED_OAUTH_CLIENTS
]
SUPPORTED_OAUTH_PROVIDERS = []
for client in _CLIENTS:
    SUPPORTED_OAUTH_PROVIDERS.append(getattr(sys.modules['loginpass'], client))

user_service = UserService


def handle_authorize(remote, token, user_info):
    user = None
    try:
        user = user_service.get_user_by_email(UserService, user_info['email'])
        user = dict_to_model(User, user)
        user.last_login_date = to_utc_datetime()
        user.save()
        user = model_to_dict(user)
    except BaseException:
        pass
    try:
        if user is None:
            user = user_service.create_user(UserService,
                                            email=user_info['email'])

        identity_object = {
            "is_user_token": True,
            "email": user_info['email'],
            "acces_token": token['access_token'],
            "user": user
        }
        access_token = create_access_token(identity=identity_object)
        success_response = make_response(redirect('/api/v1/docs'))
        success_response.set_cookie('jwt', access_token)

        return success_response
    except Exception as err:
        return ErrorObject.create_response(UserService, err.args[0],
                                           err.args[1])


@api.route('/')
class SetupLoginRoutes(Resource):
    def get(self):
        """Retrieves login providers"""

        providers = []
        for provider in SUPPORTED_OAUTH_PROVIDERS:
            providers.append(provider.OAUTH_NAME)
        resp = Response(
            render_template('login.html',
                            SUPPORTED_OAUTH_PROVIDERS=providers,
                            FLASK_TITLE=_FLASK_APP_NAME))
        return resp


@api.route('/logout')
class LogOut(Resource):
    # TODO: Clear session on logout
    pass
