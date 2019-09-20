import os
from pathlib import Path

from dotenv import load_dotenv
from flask_restplus import Api

from routes.access_point import api as access_point_api

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

api = Api(version=os.getenv("FLASK_API_VERSION").strip()
          if os.getenv("FLASK_API_VERSION").strip() else "1.0.0",
          title='Project Olympic API',
          description='All the available endpoints of Project Olympic',
          doc=os.getenv("SWAGGER_DOC_ENDPOINT").strip()
          if os.getenv("SWAGGER_DOC_ENDPOINT") else "/docs/")

api.add_namespace(access_point_api)