# from authlib.flask.client import OAuth
from flask import redirect, url_for, render_template_string, Response, jsonify
from flask_restplus import Namespace, Resource, fields
from loginpass import Google, GitHub

# from settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

api = Namespace('auth', description="Auth related operations")
SUPPORTED_OAUTH_PROVIDERS = [Google, GitHub]

def handle_authorize(remote, token, user_info):
    return jsonify(user_info)

@api.route('/')
class GetRoutes(Resource):
    def get(self):
        tpl = '<li><a href="/{}/login">{}</a></li>'
        lis = [tpl.format(b.OAUTH_NAME, b.OAUTH_NAME) for b in SUPPORTED_OAUTH_PROVIDERS]
        resp = Response('<ul>{}</ul>'.format(''.join(lis)), mimetype='text/html')
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
