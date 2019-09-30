from http import HTTPStatus

from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.helpers import ErrorObject, SuccessObject, is_user_check
from app.services import UserService

api = Namespace('user', description="User related operations")

# TODO: add DI
user_service = UserService

username_dto = api.model(
    'User\'s username', {
        'username': fields.String(description="Username", example="hunter2")
    }
)


@jwt_required
@api.doc(security='JWT')
@api.route('/')
class UserResource(Resource):
    @api.expect(username_dto)
    @is_user_check
    def post(self):
        """Sets the username of the logged in user"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    user_service.set_username(
                        self, token['user']['id'], api.payload['username'])
                )
            )
        except Exception as err:
            print(err)
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required
@api.doc(security='JWT')
@api.route('/<name>')
@api.param('name', 'Username of the user')
class GetUserResource(Resource):
    # @api.doc('get_user_by_username')
    def get(self, name: str):
        """Retrieves user by username"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    user_service.get_user_by_username(self, name)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required
@api.doc(security='JWT')
@api.route('/<name>/access-points')
@api.param('name', 'Username of user')
class UserAccessPointsResource(Resource):
    # @api.doc('get_access_points_by_user')
    # @api.marshal_list_with(base_model)
    def get(self, name: str):
        """Retrieves access points created by user"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    user_service.get_access_point_by_user(self, name)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
