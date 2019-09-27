from http import HTTPStatus

from flask import jsonify, request
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.helpers import ErrorObject, SuccessObject, convert_input_to_tuple
from app.services import AccessPointService

api = Namespace('access-points', description="Access point related operations")

user = api.inherit(
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
        'description':
        fields.String(description="Description of access point",
                      example="Near the entrance"),
        'user':
        fields.Nested(user)
    })

# TODO: Add DI
access_point_service = AccessPointService


@api.route('/')
class GetAllAccessPoints(Resource):
    @api.doc('get_all_access_points')
    # @api.marshal_list_with({object}) # marshal is able to format the responses
    def get(self):
        """Fetches all access points"""
        # return access_point_service.get_all_access_points(self)
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    access_point_service.get_all_access_points(self)))
        except Exception as err:
            print(err)
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    # decorator that transform the payload dictionary to an object
    # decorator that jsonifies all the output and returns it
    @jwt_required
    @api.doc(security='JWT')
    @api.doc('create_access_point')
    @api.expect(create_access_point_dto)
    @convert_input_to_tuple
    def post(self, **kwargs):
        current_user = get_jwt_identity()
        print(current_user)
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    access_point_service.add_access_point(self, kwargs['tupled_output'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@api.route('/<id>')
@api.param('id', 'The identifier of the access point')
@api.response(404, 'Access point not found')
class GetAccessPoint(Resource):
    @api.doc('get_access_point')
    def get(self, id):
        """Fetch a single access point"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    access_point_service.get_one_access_point(self, id)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
