from http import HTTPStatus
from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request, get_jwt_identity
)

from .object_helper import ErrorObject


def is_user_check(fn):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt_identity()
        if token['is_user_token'] is False:
            return ErrorObject.create_response(
                ErrorObject, HTTPStatus.FORBIDDEN, 'Unable to access this resource with provided token'
            )
        else:
            return fn(*args, **kwargs)
    return wrapper
