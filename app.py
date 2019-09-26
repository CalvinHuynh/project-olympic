from flask import Flask

from models import initialize_database
from routes import api
from settings import FLASK_APP_NAME, FLASK_SECRET_KEY

initialize_database()
# TODO: Compare the pros and cons of a dot env file versus configuration file
# app.config.from_object('config.Configuration')

app = Flask(FLASK_APP_NAME if FLASK_APP_NAME else __name__)

# app.config['JSON_SORT_KEYS'] = os.getenv("FLASK_SORT_JSON_KEYS").strip()
# if os.getenv("FLASK_SORT_JSON_KEYS").strip() else True
app.config['RESTPLUS_VALIDATE'] = True
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

# Initializes the routes
api.init_app(app)

if __name__ == "__main__":
    app.run()
