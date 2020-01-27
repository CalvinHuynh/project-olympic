from http import HTTPStatus

from flask import jsonify, request
from flask_restplus import Namespace, Resource

from api.helpers import ErrorObject, SuccessObject, jwt_required_extended
from api.services import ForecastService as _ForecastService

from api.settings import FLASK_ENV

api = Namespace('forecast', description="Forecast related operations")


@api.doc(security='JWT')
@api.route('')
class ForecastResources(Resource):
    @jwt_required_extended
    @api.param('number_of_weeks',
               type=int,
               description=f'Number of weeks to use for creating'
               f' the prediction model'
               )
    def post(self, **kwargs):
        """Creates next week crowd forecast"""
        if FLASK_ENV == 'development':
            try:
                return jsonify(
                    SuccessObject.create_response(
                        self, HTTPStatus.OK,
                        _ForecastService.create_next_week_prediction(
                            self,
                            number_of_weeks_to_use=request.args.get(
                                'number_of_weeks'))))
            except Exception as err:
                return ErrorObject.create_response(
                    self,
                    err.args[0],
                    err.args[1])
        else:
            return ErrorObject.create_response(
                self,
                HTTPStatus.NOT_FOUND,
                HTTPStatus.NOT_FOUND.phrase)

    @jwt_required_extended
    @api.param('start_date',
               type=str,
               description='Start date in YYYY-mm-dd format, e.g: "2019-12-31"'
               )
    @api.param('end_date',
               type=str,
               description='End date in YYYY-mm-dd format, e.g: "2019-12-31"')
    @api.param('get_dataframe',
               type=bool,
               default=False,
               enum=(True, False),
               description='Returns a jsonified dataframe if set to True')
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
