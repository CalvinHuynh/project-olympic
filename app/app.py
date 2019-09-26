from authlib.flask.client import OAuth
from flask import Flask

from app.models import initialize_database
from app.routes import blueprint as api_v1

from settings import (FLASK_APP_NAME, FLASK_SECRET_KEY, GITHUB_CLIENT_ID,
                      GITHUB_CLIENT_SECRET, GOOGLE_CLIENT_ID,
                      GOOGLE_CLIENT_SECRET)

initialize_database()

app = Flask(FLASK_APP_NAME if FLASK_APP_NAME else __name__)

app.config['RESTPLUS_VALIDATE'] = True
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
app.config['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET
app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET

oauth = OAuth(app)
# github_oauth = OAuth()

# github_oauth.register(
#     name='github',
#     client_id=GITHUB_CLIENT_ID,
#     client_secret=GITHUB_CLIENT_SECRET,
#     access_token_url='https://github.com/login/oauth/access_token',
#     authorize_url='https://github.com/login/oauth/authorize',
#     api_base_url='https://api.github.com/',
#     client_kwargs={'scope': 'user:email'})

# # Initializes oauth
# github_oauth.init_app(app)

# google_oauth = OAuth()

# GOOGLE_API_URL = 'https://www.googleapis.com/'
# GOOGLE_TOKEN_URL = GOOGLE_API_URL + 'oauth2/v4/token'
# GOOGLE_AUTH_URL = ('https://accounts.google.com/o/oauth2/v2/auth'
#                    '?access_type=offline')

# google_oauth.register(name='google',
#                       client_id=GOOGLE_CLIENT_ID,
#                       client_secret=GOOGLE_CLIENT_SECRET,
#                       access_token_url=GOOGLE_TOKEN_URL,
#                       authorize_url=GOOGLE_AUTH_URL,
#                       api_base_url=GOOGLE_API_URL,
#                       client_kwargs={'scope': 'openid email profile'})

# google_oauth.init_app(app)

# Initializes the routes
# api.init_app(app)
app.register_blueprint(api_v1)

if __name__ == "__main__":
    app.run()
