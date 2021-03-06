from flask import render_template, Response
from flask_restplus import Namespace, Resource

from api.settings import FLASK_APP_NAME as _FLASK_APP_NAME

api = Namespace('', description="Operations at index")


@api.route('/')
class Index(Resource):
    def get(self):
        """Retrieves landing page"""
        resp = Response(
            render_template('index.html',
                            FLASK_APP_NAME=_FLASK_APP_NAME,
                            FLASK_TITLE=_FLASK_APP_NAME))
        return resp
