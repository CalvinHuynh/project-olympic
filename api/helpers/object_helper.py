from api.settings import FLASK_API_VERSION

api_version = FLASK_API_VERSION if FLASK_API_VERSION else "1.0.0"


class ErrorObject:
    """An helper that creates the error response.

    Returns:
        ErrorObject -- Object containing the error with a message and a
        corresponding status code
    """
    def create_response(self, error_code, error_message: str):
        return ({
            "apiVersion": api_version,
            "error": {
                "code": error_code,
                "message": error_message
            }
        }, error_code)


class SuccessObject:
    """An helper that creates a succesful response.

    Returns:
        SuccessObject -- Object containg the data when the response is
        successful
    """
    def create_response(self, status_code, data: object):
        return {"apiVersion": api_version, "data": data}
