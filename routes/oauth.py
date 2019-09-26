from authlib.flask.client import OAuth
from flask import redirect, render_template, url_for
from flask_restplus import Namespace, Resource, fields

from settings import CLIENT_ID, CLIENT_SECRET

api = Namespace('auth', description="Auth related operations")

@api.route('/')
class Authentication(Resource):
    def get(self):
        from app import oauth
        redirect_uri = url_for('auth_authorize', _external=True)
        return oauth.github.authorize_redirect(redirect_uri)
    

@api.route('/authorize')
class Authorize(Resource):
    def get(self):
        from app import oauth
        token = oauth.github.authorize_access_token()
        print(token)
        resp = oauth.github.get('user')
        print(resp)
        profile = resp.json()
        print(profile)
        # do something with the token and profile
        return redirect('/')
