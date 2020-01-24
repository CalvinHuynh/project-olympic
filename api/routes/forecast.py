from http import HTTPStatus

from flask import jsonify, request
from flask_restplus import Namespace, Resource

from api.helpers import ErrorObject, SuccessObject, jwt_required_extended
from api.services import ForecastService as _ForecastService

api = Namespace('forecast', description="Forecast related operations")


@api.doc(security='JWT')
@api.route('')
class ForecastResources(Resource):
    @jwt_required_extended
    def post(self, **kwargs):
        """Creates next week crowd forecast"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _ForecastService.create_next_week_prediction(self)))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])

    @jwt_required_extended
    @api.param('start_date',
               type=str,
               description='Start date in YYYY-mm-dd format, e.g: "2019-12-31"'
               )
    @api.param('end_date',
               type=str,
               description='End date in YYYY-mm-dd format, e.g: "2019-12-31"')
    @api.param('get_dataframe',
               type=int,
               default=0,
               enum=(0, 1),
               description='Returns a jsonified dataframe if set to 1')
    def get(self, **kwargs):
        """Retrieves crowd forecast per week"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _ForecastService.get_crowd_forecast(
                        self,
                        start_date=request.args.get('start_date'),
                        end_date=request.args.get('end_date'),
                        return_data_frame=request.args.get('get_dataframe'))))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
