from http import HTTPStatus
from flask import redirect, url_for, render_template, Response, jsonify, make_response
from flask_restplus import Namespace, Resource, fields
from loginpass import Google, GitHub
from flask_jwt_extended import create_access_token

from app.services import UserService
from app.helpers import ErrorObject, SuccessObject

api = Namespace('auth', description="Auth related operations")
SUPPORTED_OAUTH_PROVIDERS = [Google, GitHub]

user_service = UserService


def handle_authorize(remote, token, user_info):
    user = None
    try:
        user = user_service.get_user_by_email(UserService, user_info['email'])
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
        print(err)
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