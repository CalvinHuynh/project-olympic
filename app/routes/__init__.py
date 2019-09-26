from flask import Blueprint, jsonify
from flask_restplus import Api
# from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint, Google, GitHub

from app.routes.access_point import api as access_point_api
from app.routes.oauth import api as oauth_api, handle_authorize
from app.routes.user import api as user_api
from app.routes.assets import api as assets_api
from settings import FLASK_API_VERSION, SWAGGER_DOC_ENDPOINT

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint,
          version=FLASK_API_VERSION if FLASK_API_VERSION else "1.0.0",
          title='Project Olympic API',
          description='All the available endpoints of Project Olympic',
          doc=SWAGGER_DOC_ENDPOINT if SWAGGER_DOC_ENDPOINT else "/docs/")

api.add_namespace(access_point_api)
api.add_namespace(user_api)
api.add_namespace(oauth_api)
api.add_namespace(assets_api)

# TODO: extract to separate file
SUPPORTED_OAUTH_PROVIDERS = [Google, GitHub]

for backend in SUPPORTED_OAUTH_PROVIDERS:
    from app.app import oauth, app
    bp = create_flask_blueprint(backend, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='/{}'.format(backend.OAUTH_NAME))