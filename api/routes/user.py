from http import HTTPStatus

from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity

from api.helpers import (ErrorObject, SuccessObject, check_for,
                         jwt_required_extended)
from api.services import (UserService as _UserService, DataSourceTokenService
                          as _DataSourceTokenService)

api = Namespace('user', description="User related operations")


username_dto = api.model(
    'SetUsernameDto',
    {'username': fields.String(description="Username", example="hunter2")})


@jwt_required_extended
@api.doc(security='JWT')
@api.route('')
class UserResource(Resource):
    @check_for("User")
    def get(self):
        """Retrieves the information of the logged in user"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _UserService.get_user_by_id(self, token['user']['id'],
                                                True)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    @api.expect(username_dto)
    @check_for("User")
    def post(self):
        """Sets the username of the logged in user"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _UserService.set_username(self, token['user']['id'],
                                              api.payload['username'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/tokens')
class UserDataSourceTokensResource(Resource):
    @check_for("User")
    def get(self):
        """Retrieves data source tokens created by the logged in user"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _UserService.get_data_source_tokens_by_user(
                        self, token['user']['id'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/tokens/<token_id>/admin-revoke')
@api.param('token_id', 'Id of token to revoke')
class UserDataSourceTokenAdminRevokeResource(Resource):
    @check_for("User")
    def post(self, token_id: int):
        """Deactivates a specific data source token"""
        token = get_jwt_identity()
        if token['user']['id'] == 1:
            try:
                return jsonify(
                    SuccessObject.create_response(
                        self, HTTPStatus.OK,
                        _DataSourceTokenService.admin_revoke_token(
                            self, token_id)))
            except Exception as err:
                return ErrorObject.create_response(self, err.args[0],
                                                   err.args[1])
        else:
            return ErrorObject.create_response(
                self, HTTPStatus.FORBIDDEN,
                "You are unable to access this endpoint.")


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/tokens/<token_id>/revoke')
@api.param('token_id', 'Id of token to revoke')
class UserDataSourceTokenRevokeResource(Resource):
    @check_for("User")
    def post(self, token_id: int):
        """Deactivates a specific data source token"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _UserService.deactivate_token_of_user(
                        self, token['user']['id'], token_id)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/<name>')
@api.param('name', 'Username of the user')
class GetUserResource(Resource):
    # @api.doc('get_user_by_username')
    @check_for("User")
    def get(self, name: str):
        """Retrieves user by username"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _UserService.get_user_by_username(self, name)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@jwt_required_extended
@api.doc(security='JWT')
@api.route('/<name>/data-source')
@api.param('name', 'Username of user')
class UserDataSourcesResource(Resource):
    # @api.marshal_list_with(base_model)
    @check_for("User")
    def get(self, name: str):
        """Retrieves data sources created by user"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _UserService.get_data_source_by_user(self,
                                                         username=name)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
