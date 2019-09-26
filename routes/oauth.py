from authlib.flask.client import OAuth
from flask import redirect, render_template, url_for
from flask_restplus import Namespace, Resource, fields

from settings import CLIENT_ID, CLIENT_SECRET

# oauth = OAuth(app)

# oauth.register(
#     name='project-olympic',
#     client_id=CLIENT_ID,
#     client_secret=CLIENT_SECRET,
#     access_token_url='https://github.com/login/oauth/access_token',
#     authorize_url='https://github.com/login/oauth/authorize',
#     api_base_url='https://api.github.com/',
#     client_kwargs={'scope': 'user:email'}
# )

api = Namespace('auth', description="Auth related operations")

@api.route('/')
class Authentication(Resource):
    def get(self):
        # redirect_uri = url_for('authorize', _external=True)
        # return oauth.github.authorize_redirect(redirect_uri)
        pass
    

@api.route('/authorize')
class Authorize(Resource):
    def get(self):
        # token = oauth.github.authorize_access_token()
        # resp = oauth.github.get('user')
        # profile = resp.json()
        # # do something with the token and profile
        # return redirect('/')
        pass
