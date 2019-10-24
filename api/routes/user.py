from http import HTTPStatus

from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity

from api.helpers import (ErrorObject, SuccessObject, is_user_check,
                         jwt_required_extended)
from api.services import (UserService as _UserService, DataSourceTokenService
                          as _DataSourceTokenService)

api = Namespace('user', description="User related operations")

# TODO: add DI
_user_service = _UserService
_data_source_token_service = _DataSourceTokenService

username_dto = api.model(
    'User\'s username',
    {'username': fields.String(description="Username", example="hunter2")})


@jwt_required_extended
@api.doc(security='JWT')
@api.route('')
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
                    _user_service.set_username(self, token['user']['id'],
                                               api.payload['username'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/tokens')
class UserDataSourceTokensResource(Resource):
    @is_user_check
    def get(self):
        """Retrieves data source tokens created by the logged in user"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _user_service.get_data_source_tokens_by_user(
                        self, token['user']['id'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/tokens/<id>/revoke')
@api.param('id', 'Id of token to revoke')
class UserDataSourceTokenRevokeResource(Resource):
    @is_user_check
    def post(self, id: int):
        """Deactivates a specific data source token"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_token_service.revoke_token(self, id)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/<name>')
@api.param('name', 'Username of the user')
class GetUserResource(Resource):
    # @api.doc('get_user_by_username')
    @is_user_check
    def get(self, name: str):
        """Retrieves user by username"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _user_service.get_user_by_username(self, name)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/<name>/data-source')
@api.param('name', 'Username of user')
class UserDataSourcesResource(Resource):
    # @api.marshal_list_with(base_model)
    @is_user_check
    def get(self, name: str):
        """Retrieves data sources created by user"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _user_service.get_data_source_by_user(self,
                                                          username=name)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
