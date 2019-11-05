from http import HTTPStatus

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from flask_restplus import Namespace, Resource, fields

from api.helpers import (ErrorObject, SuccessObject, convert_input_to_tuple,
                         token_is_active_check, jwt_required_extended)
from api.services import (DataSourceDataService as _DataSourceDataService,
                          WeatherService as _WeatherService)

api = Namespace('data', description="Data related operations")

create_data_source_data_dto = api.model('CreateDataSourceDataDto', {
    'no_of_clients':
    fields.Integer(description="number of clients", example=4),
})

_data_source_data_service = _DataSourceDataService
_weather_service = _WeatherService


@api.doc(security='JWT')
@api.route('')
class DataResources(Resource):
    @jwt_required_extended
    @api.param('limit',
               type=int,
               default=20,
               description='Limits the number of result to return')
    @api.param('start_date',
               type=str,
               description='Start date in YYYY-mm-dd format, e.g: "2019-12-31"'
               )
    @api.param('end_date',
               type=str,
               description='End date in YYYY-mm-dd format, e.g: "2019-12-31"')
    @api.param('order_by',
               type=str,
               default='desc',
               enum=('desc', 'asc'),
               description='orders the result by primary key')
    def get(self):
        """Fetches all data points"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _data_source_data_service.get_all_data(
                        self,
                        limit=request.args.get('limit'),
                        start_date=request.args.get('start_date'),
                        end_date=request.args.get('end_date'),
                        order_by=request.args.get('order_by')), True))
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
                    _data_source_data_service.post_data(
                        self, token['data_source_token']['data_source']['id'],
                        kwargs['tupled_output'])))
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
    @api.param('limit',
               type=int,
               default=20,
               description='Limits the number of results')
    @api.param('start_date',
               type=str,
               description='Start date in YYYY-mm-dd format, e.g: "2019-12-31"'
               )
    @api.param('end_date',
               type=str,
               description='End date in YYYY-mm-dd format, e.g: "2019-12-31"')
    @api.param('order_by',
               type=str,
               default='desc',
               enum=('desc', 'asc'),
               description='Orders the result by id')
    @api.param('forecast_type',
               type=str,
               default='all',
               enum=('hourly', 'weekly', 'all'),
               help='Filters result by type.')
    def get(self):
        """Fetches all weather data"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _weather_service.retrieve_all_weather_data(
                        self,
                        limit=request.args.get('limit'),
                        start_date=request.args.get('start_date'),
                        end_date=request.args.get('end_date'),
                        order_by=request.args.get('order_by'),
                        forecast_type=request.args.get('forecast_type')),
                    True))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
