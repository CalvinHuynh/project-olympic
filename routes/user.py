from http import HTTPStatus

from flask import jsonify
from flask_restplus import Namespace, Resource, fields

from helpers import ErrorObject, SuccessObject
from services import UserService

api = Namespace('', description="User related operations")

# TODO: add DI
user_service = UserService


# access_point = api.model(
#     'AccessPointByUser', {
#         'id':
#         fields.Integer(description="Id of access point", example=2),
#         'description':
#         fields.String(description="Description of access point",
#                       example="Near the entrance"),
#     })

# base_model = api.model('BaseResponse', {
#     'apiVersion': fields.String(description="API version", example="0.0.1"),
#     'data': [fields.Nested(access_point)]
# })


@api.route('/<name>')
@api.param('name', 'Username of the user')
class GetUser(Resource):
    @api.doc('get_user_by_username')
    def get(self, name: str):
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    user_service.get_user_by_username(self, name)))
        except Exception as err:
            try:
                status_code = err.args[1]
            except IndexError:
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR

            return ErrorObject.create_response(self, err.args[0], status_code)


@api.route('/<name>/access-points')
@api.param('name', 'Username of user')
class GetUserAccessPoints(Resource):
    @api.doc('get_access_points_by_user')
    # @api.marshal_list_with(base_model)
    def get(self, name: str):
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    user_service.get_access_point_by_user(self, name)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
