from http import HTTPStatus

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from flask_restplus import Namespace, Resource, fields

from api.helpers import (ErrorObject, SuccessObject, convert_input_to_tuple,
                         jwt_required_extended, check_for)
from api.services import (DataSourceDataService as _DataSourceDataService,
                          WeatherService as _WeatherService)

api = Namespace('data', description="Data related operations")

create_data_source_data_dto = api.model('CreateDataSourceDataDto', {
    'no_of_clients':
    fields.Integer(description="number of clients", example=4),
})


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
    @api.param('sort',
               type=str,
               default='desc',
               enum=('desc', 'asc'),
               description='Sorts the result in ascending or descending order')
    def get(self):
        """Fetches data from all sources"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _DataSourceDataService.get_all_data(
                        self,
                        limit=request.args.get('limit'),
                        start_date=request.args.get('start_date'),
                        end_date=request.args.get('end_date'),
                        sort=request.args.get('sort')), True))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    @jwt_required_extended
    @api.expect(create_data_source_data_dto)
    @convert_input_to_tuple
    @check_for("Machine")
    def post(self, **kwargs):
        """Creates new data"""
        token = get_jwt_identity()
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _DataSourceDataService.post_data(
                        self, token['data_source_token']['data_source'],
                        kwargs['tupled_output'])))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@api.doc(security='JWT')
@api.route('/source/<data_source_id>')
@api.param('data_source_id', 'The identifier of the data source')
class SpecificDataSourceResource(Resource):
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
    @api.param('sort',
               type=str,
               default='desc',
               enum=('desc', 'asc'),
               description='Sorts the result in ascendig or descending order')
    def get(self, data_source_id):
        """Fetches all data from a single data source"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _DataSourceDataService.get_all_data_from_data_source(
                        self,
                        data_source_id=data_source_id,
                        limit=request.args.get('limit'),
                        start_date=request.args.get('start_date'),
                        end_date=request.args.get('end_date'),
                        sort=request.args.get('sort')), True))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])


@api.doc(security='JWT')
@api.route('/<data_id>')
@api.param('data_id', 'The identifier of the data point')
class SincleDataResources(Resource):
    @jwt_required_extended
    def get(self, data_id):
        """Fetch a single data point"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _DataSourceDataService.get_one_data_point(
                        self, data_id)))
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
               default='id',
               enum=('id', 'created_date'),
               description='orders the result by field')
    @api.param('sort',
               type=str,
               default='desc',
               enum=('desc', 'asc'),
               description='Sorts the result in ascending or descending order')
    @api.param('forecast_type',
               type=str,
               default='all',
               enum=('hourly', 'weekly', 'all'),
               description='Filters result by type.')
    def get(self):
        """Fetches all weather data"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _WeatherService.retrieve_all_weather_data(
                        self,
                        limit=request.args.get('limit'),
                        start_date=request.args.get('start_date'),
                        end_date=request.args.get('end_date'),
                        order_by=request.args.get('order_by'),
                        sort=request.args.get('sort'),
                        forecast_type=request.args.get('forecast_type')),
                    True))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
