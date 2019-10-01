from http import HTTPStatus
from datetime import datetime

from flask import (Response, jsonify, make_response, redirect, render_template,
                   url_for)
from flask_jwt_extended import create_access_token
from flask_restplus import Namespace, Resource, fields
from loginpass import GitHub, Google
from playhouse.shortcuts import dict_to_model, model_to_dict

from app.helpers import ErrorObject, SuccessObject
from app.models import User
from app.services import UserService

api = Namespace('auth', description="Auth related operations")
SUPPORTED_OAUTH_PROVIDERS = [Google, GitHub]

user_service = UserService


def handle_authorize(remote, token, user_info):
    user = None
    try:
        user = user_service.get_user_by_email(UserService, user_info['email'])
        user = dict_to_model(User, user)
        user.last_login_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        user.save()
        user = model_to_dict(user)
    except:
        pass
    try:
        if user is None:
            user = user_service.create_user(
                UserService, email=user_info['email'])

        identity_object = {
            "is_user_token": True,
            "email": user_info['email'],
            "acces_token": token['access_token'],
            "user": user
        }
        access_token = create_access_token(identity=identity_object)
        success_response = make_response(redirect('/api/v1/docs'))
        success_response.set_cookie('jwt', 'Bearer {}'.format(access_token))

        return success_response
        # return jsonify(
        #     SuccessObject.create_response(
        #         UserService, HTTPStatus.OK, {"jwt": access_token})
        # )
    except Exception as err:
        return ErrorObject.create_response(UserService, err.args[0], err.args[1])


@api.route('/')
class SetupLoginRoutes(Resource):
    def get(self):
        """Retrieves login providers"""
        tpl = '<a href="/{}/login"><button type="button">{}</button></a><br/><br/>'
        lis = [tpl.format(b.OAUTH_NAME, b.OAUTH_NAME)
               for b in SUPPORTED_OAUTH_PROVIDERS]
        print(lis)
        resp = Response(render_template(
            'login.html', SUPPORTED_OAUTH_PROVIDERS='<ul>{}</ul>'.format(''.join(lis))))
        return resp

@api.route('/logout')
class LogOut(Resource):
    pass
