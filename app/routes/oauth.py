from authlib.flask.client import OAuth
from flask import redirect, render_template, url_for
from flask_restplus import Namespace, Resource, fields

from settings import CLIENT_ID, CLIENT_SECRET

api = Namespace('auth', description="Auth related operations")

@api.route('/github')
class GithubAuthentication(Resource):
    def get(self):
        from app.app import github_oauth
        redirect_uri = url_for('auth_authorize', _external=True)
        return github_oauth.github.authorize_redirect(redirect_uri)
    

@api.route('/github/authorize')
class GithubAuthorize(Resource):
    def get(self):
        from app.app import github_oauth
        token = github_oauth.github.authorize_access_token()
        print(token)
        resp = github_oauth.github.get('user')
        print(resp)
        profile = resp.json()
        print(profile)
        # do something with the token and profile
        return redirect('/')

@api.route('/google')
class GoogleAuthentication(Resource):
    def get(self):
        pass

@api.route('/google/authorize')
class GoogleAuthorize(Resource):
    def get(self):
        pass