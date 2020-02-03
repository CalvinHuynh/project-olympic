import sys

from flask import (Response, make_response, redirect, render_template, session)
from flask_jwt_extended import (create_access_token, set_access_cookies,
                                unset_access_cookies)
from flask_restplus import Namespace, Resource
from loginpass import __all__ as _LOGINPASS_OAUTH_BACKENDS
from playhouse.shortcuts import dict_to_model, model_to_dict

from api.helpers import ErrorObject, to_utc_datetime
from api.models import User
from api.services import UserService as _UserService
from api.settings import (ALLOWED_OAUTH_CLIENTS as _ALLOWED_OAUTH_CLIENTS,
                          FLASK_APP_NAME as _FLASK_APP_NAME)

api = Namespace('auth', description="Auth related operations")
_CLIENTS = [
    i for i in _LOGINPASS_OAUTH_BACKENDS if i.lower() in _ALLOWED_OAUTH_CLIENTS
]
SUPPORTED_OAUTH_PROVIDERS = []
for client in _CLIENTS:
    SUPPORTED_OAUTH_PROVIDERS.append(getattr(sys.modules['loginpass'], client))


def handle_authorize(remote, token, user_info):
    user = None
    try:
        user = _UserService.get_user_by_email(_UserService, user_info['email'])
        user = dict_to_model(User, user)
        user.last_login_date = to_utc_datetime()
        user.save()
        user = model_to_dict(user)
    except BaseException:
        pass
    try:
        if user is None:
            user = _UserService.create_user(_UserService,
                                            email=user_info['email'])

        identity_object = {
            "is_user_token": True,
            "email": user_info['email'],
            "acces_token": token['access_token'],
            "user": user
        }
        access_token = create_access_token(identity=identity_object)
        response = make_response(redirect('/'))
        session["user"] = user
        print(session["user"])
        set_access_cookies(response, access_token)

        return response
    except Exception as err:
        return ErrorObject.create_response(_UserService, err.args[0],
                                           err.args[1])


@api.route('/')
class SetupLoginRoutes(Resource):
    def get(self):
        """Retrieves login providers"""

        providers = []
        for provider in SUPPORTED_OAUTH_PROVIDERS:
            providers.append(provider.OAUTH_NAME)
        response = Response(
            render_template('login.html',
                            SUPPORTED_OAUTH_PROVIDERS=providers,
                            FLASK_TITLE=_FLASK_APP_NAME))
        return response


@api.route('/logout')
class LogOut(Resource):
    def get(self):
        """Log out the current user"""
        response = make_response(redirect('/'))
        # unset_jwt_cookies(response)
        session.pop("user", None)
        unset_access_cookies(response)
        return response
