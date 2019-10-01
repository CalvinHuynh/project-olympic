from http import HTTPStatus
from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request, get_jwt_identity
)

from .object_helper import ErrorObject

"""A wrapper that checks if the provided JWT is a user token
"""


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


"""A wrapper that checks if the provided JWT is an access token
"""


def token_is_active_check(fn):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt_identity()
        if token['is_user_token'] is False:
            if token['access_point_token']['is_active'] is False:
                return ErrorObject.create_response(
                    ErrorObject, HTTPStatus.FORBIDDEN, 'Unable to access this resource with provided token'
                )
            else:
                from app.services.access_point_token import AccessPointTokenService
                AccessPointTokenService.update_hit_count_and_date(
                    AccessPointTokenService, token['access_point_token']['id'])
                return fn(*args, **kwargs)
        else:
             return ErrorObject.create_response(
                 ErrorObject, HTTPStatus.FORBIDDEN, 'Unable to access this resource with provided token'
             )
    return wrapper
