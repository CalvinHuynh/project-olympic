# from authlib.flask.client import OAuth
from http import HTTPStatus
from flask import redirect, url_for, render_template_string, Response, jsonify
from flask_restplus import Namespace, Resource, fields
from loginpass import Google, GitHub
from flask_jwt_extended import create_access_token

from app.services import UserService
from app.helpers import ErrorObject, SuccessObject

# from settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

api = Namespace('auth', description="Auth related operations")
SUPPORTED_OAUTH_PROVIDERS = [Google, GitHub]

user_service = UserService

def handle_authorize(remote, token, user_info):
    print("************** remote ************")
    print(remote)
    print("************** token ************")
    print(token)
    print("************** user info ************")
    print(user_info)
    
    identity_object = {
        "email": user_info['email'],
        "acces_token": token['access_token'],
    }
    try:
        user_service.create_user(UserService, email=user_info['email'])
        access_token = create_access_token(identity=identity_object)
        print(access_token)
        return jsonify(
            SuccessObject.create_response(UserService, HTTPStatus.OK, {"jwt": access_token})
        )
    except Exception as err:
        return ErrorObject.create_response(UserService, err.args[0], err.args[1])
 

@api.route('/')
class GetLoginRoutes(Resource):
    def get(self):
        tpl = '<li><a href="/{}/login">{}</a></li>'
        lis = [tpl.format(b.OAUTH_NAME, b.OAUTH_NAME) for b in SUPPORTED_OAUTH_PROVIDERS]
        resp = Response('<ul>{}</ul>'.format(''.join(lis)))
        return resp

# @api.route('/github')
# class GithubAuthentication(Resource):
#     def get(self):
#         from app.app import github_oauth
#         redirect_uri = url_for('auth_github_authorize', _external=True)
#         return github_oauth.github.authorize_redirect(redirect_uri)


# @api.route('/github/authorize')
# class GithubAuthorize(Resource):
#     def get(self):
#         from app.app import github_oauth
#         token = github_oauth.github.authorize_access_token()
#         print(token)
#         resp = github_oauth.github.get('user')
#         print(resp)
#         profile = resp.json()
#         print(profile)
#         # do something with the token and profile
#         return redirect('/')


# @api.route('/google')
# class GoogleAuthentication(Resource):
#     def get(self):
#         from app.app import google_oauth
#         redirect_uri = url_for('auth_google_authorize')
#         return google_oauth.google.authorize_redirect(redirect_uri)
#         # pass


# @api.route('/google/authorize')
# class GoogleAuthorize(Resource):
#     def get(self):
#         from app.app import google_oauth
#         token = google_oauth.google.authorize_access_token()
#         print(token)
#         resp = google_oauth.google.get('user')
#         print(resp)
#         profile = resp.json()
#         print(profile)
#         # do something with the token and profile
#         return redirect('/')
