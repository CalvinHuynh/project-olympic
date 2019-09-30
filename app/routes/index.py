import os
from flask import render_template, Response
from flask_restplus import Namespace, Resource, fields

from settings import FLASK_APP_NAME

api = Namespace('', description="Operations at index")

@api.route('/')
class Index(Resource):
    def get(self):
        """Retrieves landing page"""
        resp = Response(render_template('index.html', FLASK_APP_NAME=FLASK_APP_NAME))
        return resp