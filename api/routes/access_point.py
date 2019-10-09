from http import HTTPStatus

from flask import jsonify, request
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity

from api.helpers import ErrorObject, SuccessObject, convert_input_to_tuple, is_user_check, jwt_required_extended
from api.services import AccessPointService, AccessPointTokenService


api = Namespace('access-points', description="Access point related operations")

user_dto = api.inherit(
    'User',
    {
        'id': fields.Integer(description="Id of user"),
        'username': fields.String(description="Username", example="admin1234"),
        # 'email':
        # fields.String(description="Email of user", example="test@test.test"),
        # 'join_date': fields.String,
        # 'last_login_date': fields.String
    })

create_access_point_dto = api.model(
    'CreateAccessPoint', {
        'ip_addr': fields.String(description="(static) IP if access point",
                                 example="localhost"),
        'description':
        fields.String(description="Description of access point",
                      example="Running on localhost"),
        'user':
        fields.Nested(user_dto)
    })

# TODO: Add DI
access_point_service = AccessPointService
access_point_token_service = AccessPointTokenService


@api.doc(security='JWT')
@api.route('/')
class AllAccessPointsResources(Resource):
    # TODO: implement actual usage of docs according to https://flask-restplus.readthedocs.io/en/stable/swagger.html
    @api.doc('get_all_access_points')
    @jwt_required_extended
    # @api.marshal_list_with({object}) # marshal is able to format the responses
    def get(self):
        """Fetches all access points"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    access_point_service.get_all_access_points(self)
                )
            )
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    @jwt_required_extended
    @api.expect(create_access_point_dto)
    @convert_input_to_tuple
    @is_user_check
    def post(self, **kwargs):
        """Creates a new access point"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    access_point_service.add_access_point(self, kwargs['tupled_output'], token['user']['id'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@api.doc(security='JWT')
@api.route('/<id>')
@api.param('id', 'The identifier of the access point')
# @api.response(404, 'Access point not found')
class SingleAccessPointResources(Resource):
    @api.doc('get_access_point')
    @jwt_required_extended
    def get(self, id):
        """Fetch a single access point"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    access_point_service.get_access_point_by_id(self, id)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    # @api.doc('post_token_for_access_point', security='JWT')
    @jwt_required_extended
    @is_user_check
    def post(self, id):
        """Creates a token for access point"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    access_point_token_service.create_token_for_access_point(
                        self, access_point_id=id, user_id=token['user']['id'])
                )
            )
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
