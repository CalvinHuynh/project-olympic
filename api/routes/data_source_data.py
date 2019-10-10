from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from flask_restplus import Namespace, Resource, fields

from api.helpers import (ErrorObject, SuccessObject, convert_input_to_tuple,
                         token_is_active_check, jwt_required_extended)
from api.services import DataSourceDataService as _DataSourceDataService, WeatherService as _WeatherService

api = Namespace('data', description="Access point data related operations")

create_data_source_data_dto = api.model(
    'CreateDataSourceDataDto', {
        'no_of_clients': fields.Integer(description="number of clients",
                                        example=4),
    })

_data_source_data_service = _DataSourceDataService
_weather_service = _WeatherService

@api.doc(security='JWT')
@api.route('/')
class DataResources(Resource):
    @jwt_required_extended
    def get(self):
        """Fetches all data points"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_data_service.get_all_data(self)
                )
            )
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    @jwt_required_extended
    @api.expect(create_data_source_data_dto)
    @convert_input_to_tuple
    @token_is_active_check
    def post(self, **kwargs):
        """Creates new data"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_data_service.post_access_point_data(
                        self, token['data_source_token']['data_source']['id'], kwargs['tupled_output'])
                )
            )
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@api.doc(security='JWT')
@api.route('/<id>')
@api.param('id', 'The identifier of the data point')
class SincleDataResources(Resource):
    @jwt_required_extended
    def get(self, id):
        """Fetch a single data point"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_data_service.get_one_data_point(self, id)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

@api.doc(security='JWT')
@api.route('/weather')
class WeatherResources(Resource):
    @jwt_required_extended
    def get(self):
        """Fetches all weather data"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _weather_service.retrieve_all_weather_data(self)
                )
            )
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
