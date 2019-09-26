from authlib.flask.client import OAuth
from flask import Flask

from models import initialize_database
from routes import api
from settings import FLASK_APP_NAME, FLASK_SECRET_KEY, CLIENT_ID, CLIENT_SECRET

initialize_database()

app = Flask(FLASK_APP_NAME if FLASK_APP_NAME else __name__)

app.config['RESTPLUS_VALIDATE'] = True
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

oauth = OAuth()

oauth.register(
    name='github',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'}
)

# Initializes oauth
oauth.init_app(app)

# Initializes the routes
api.init_app(app)

if __name__ == "__main__":
    api.run()
