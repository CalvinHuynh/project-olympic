from flask import Blueprint
from flask_restplus import Api
from loginpass import create_flask_blueprint, Google, GitHub

from api.routes.data_source import api as data_source_api
from api.routes.login import api as login_api, handle_authorize
from api.routes.user import api as user_api
# from api.routes.assets import api as assets_api
from api.routes.index import api as index_api
# data generated from the data source
from api.routes.data_source_data import api as data_source_data_api
from api.settings import (FLASK_API_VERSION, SWAGGER_DOC_ENDPOINT, GET_PATH,
                          FLASK_APP_NAME)

authorizations = {
    'JWT': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description':
        "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, \
            where JWT is the token"
    }
}

templates_folder_path = GET_PATH() + '/templates'
blueprint_index = Blueprint('index',
                            __name__,
                            url_prefix='',
                            template_folder=templates_folder_path)
api_index = Api(blueprint_index)

api_index.add_namespace(index_api)

blueprint_api = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint_api,
          version=FLASK_API_VERSION if FLASK_API_VERSION else "1.0.0",
          title=f"{FLASK_APP_NAME} API",
          description='All the available endpoints of Project Olympic',
          doc=SWAGGER_DOC_ENDPOINT if SWAGGER_DOC_ENDPOINT else "/docs/",
          authorizations=authorizations)

api.add_namespace(data_source_api)
api.add_namespace(user_api)
api.add_namespace(login_api)
api.add_namespace(data_source_data_api)
# api.add_namespace(assets_api)

# TODO: extract to separate file
SUPPORTED_OAUTH_PROVIDERS = [Google, GitHub]

for backend in SUPPORTED_OAUTH_PROVIDERS:
    from api.app import app
    from api.app_setup import oauth

    bp = create_flask_blueprint(backend, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='/{}'.format(backend.OAUTH_NAME))
