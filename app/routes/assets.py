# import os
# from flask import send_from_directory
# from flask_restplus import Namespace, Resource, fields

# api = Namespace('', description="Path to assets")

# @api.route('/favicon.ico')
# class GetFavicon(Resource):
#     def get(self):
#         from app.app import app
#         return send_from_directory(os.path.join(app.root_path, 'assets'),
#                             'favicon.ico',mimetype='image/x-icon')