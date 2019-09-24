from flask_restplus import Namespace, Resource
from flask import jsonify
from http import HTTPStatus

from services import UserService
from helpers import ErrorObject, SuccessObject

api = Namespace('', description="User related operations")

user_service = UserService

@api.route('/<name>')
@api.param('name', 'Username of the user')
class GetUser(Resource):
    @api.doc('get_user_by_username')
    def get(self, name: str):
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    user_service.get_user_by_username(self, name)
                )
            )
        except Exception as err:
            try:
                status_code = err.args[1]
            except IndexError:
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR

            return ErrorObject.create_response(self, err.args[0], status_code)
