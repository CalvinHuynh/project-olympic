
from flask_restplus import Api

from routes.access_point import api as access_point_api
from routes.oauth import api as oauth_api
from routes.user import api as user_api
from routes.assets import api as assets_api
from settings import FLASK_API_VERSION, SWAGGER_DOC_ENDPOINT

api = Api(version=FLASK_API_VERSION if FLASK_API_VERSION else "1.0.0",
          title='Project Olympic API',
          description='All the available endpoints of Project Olympic',
          doc=SWAGGER_DOC_ENDPOINT if SWAGGER_DOC_ENDPOINT else "/docs/")

api.add_namespace(access_point_api)
api.add_namespace(user_api)
api.add_namespace(oauth_api)
api.add_namespace(assets_api)
