from http import HTTPStatus

from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity

from api.helpers import (ErrorObject, SuccessObject, convert_input_to_tuple,
                         is_user_check, jwt_required_extended)
from api.services import (DataSourceService as _DataSourceService,
                          DataSourceTokenService as _DataSourceTokenService)

api = Namespace('source', description="Data sources related operations")

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

create_data_source_dto = api.model(
    'CreateDataSource',
    {
        'source':
        fields.String(description="description of the data source",
                      example="cronjob @ localhost"),
        'description':
        fields.String(description="Description of the data source",
                      example="Running on localhost"),
        # 'user':
        # fields.Nested(user_dto)
    })

# TODO: Add DI
_data_source_service = _DataSourceService
_data_source_token_service = _DataSourceTokenService


@api.doc(security='JWT')
@api.route('/')
class AllDataSourcesResources(Resource):
    # TODO: implement actual usage of docs according to
    # https://flask-restplus.readthedocs.io/en/stable/swagger.html
    @jwt_required_extended
    def get(self):
        """Fetches all data sources"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_service.get_all_data_sources(self)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    @jwt_required_extended
    @api.expect(create_data_source_dto)
    @convert_input_to_tuple
    @is_user_check
    def post(self, **kwargs):
        """Creates a new data source"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_service.add_data_source(
                        self, kwargs['tupled_output'], token['user']['id'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@api.doc(security='JWT')
@api.route('/<id>')
@api.param('id', 'The identifier of the data source')
# @api.response(404, 'Data source not found')
class SingleDataSourceResource(Resource):
    @jwt_required_extended
    def get(self, id):
        """Fetch a single data source"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_service.get_data_source_by_id(self, id)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    @jwt_required_extended
    @is_user_check
    def post(self, id):
        """Creates a token for data source"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_token_service.create_token_for_data_source(
                        self, data_source_id=id, user_id=token['user']['id'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
