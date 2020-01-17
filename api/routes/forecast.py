from http import HTTPStatus

from flask import jsonify
# from flask_jwt_extended import get_jwt_identity
from flask_restplus import Namespace, Resource

from api.helpers import ErrorObject, SuccessObject, jwt_required_extended
from api.services import ForecastService as _ForecastService

api = Namespace('forecast', description="Forecast related operations")


@api.doc(security='JWT')
@api.route('')
class ForecastResources(Resource):
    @jwt_required_extended
    # @convert_input_to_tuple
    # @check_for("User")
    def post(self, **kwargs):
        """Creates next week prediction"""
        try:
            return jsonify(
                SuccessObject.create_response(
                    self, HTTPStatus.OK,
                    _ForecastService.create_next_week_prediction()))
        except Exception as err:
            return ErrorObject.create_response(self, err.args[0], err.args[1])
