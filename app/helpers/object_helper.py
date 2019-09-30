from http import HTTPStatus

from settings import FLASK_API_VERSION

api_version = FLASK_API_VERSION if FLASK_API_VERSION else "1.0.0"


class ErrorObject:
    def create_response(self, error_code, error_message: str):
        return ({
            "apiVersion": api_version,
            "error": {
                "code": error_code,
                "message": error_message
            }
        }, error_code)


class SuccessObject:
    def create_response(self, status_code, data: object):
        return {"apiVersion": api_version, "data": data}
