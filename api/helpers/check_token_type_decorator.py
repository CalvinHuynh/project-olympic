from functools import wraps
from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import (get_jwt_identity, jwt_required,
                                verify_jwt_in_request)

from .object_helper import ErrorObject

original_jwt_required = jwt_required

def _token_usage_counter_add(token_id: int):
    from api.services.data_source_token import DataSourceTokenService
    DataSourceTokenService.update_hit_count_and_date(
                    DataSourceTokenService, token_id)

def jwt_required_extended(fn):
    """
    A custom decorator that extends the functionality of the jwt_required function
    from the package flask_jwt_extended
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt_identity()
        if token['is_user_token'] is False:
            from api.services.data_source_token import DataSourceTokenService
            if DataSourceTokenService.check_if_token_is_active(DataSourceTokenService, token['data_source_token']['id']):
                _token_usage_counter_add(token['data_source_token']['id'])
        return fn(*args, **kwargs)
    return wrapper


def is_user_check(fn):
    """
    A wrapper that checks if the provided JWT is a user token
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt_identity()
        if token['is_user_token'] is False:
            _token_usage_counter_add(token['data_source_token']['id'])
            return ErrorObject.create_response(
                ErrorObject, HTTPStatus.FORBIDDEN, 'Unable to access this resource with provided token'
            )
        else:
            return fn(*args, **kwargs)
    return wrapper


def token_is_active_check(fn):
    """
    A wrapper that checks if the provided JWT is an access token
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt_identity()
        if token['is_user_token'] is False:
            from api.services.data_source_token import DataSourceTokenService
            _token_usage_counter_add(token['data_source_token']['id'])
            if DataSourceTokenService.check_if_token_is_active(DataSourceTokenService, token['data_source_token']['id']) is False:
                return ErrorObject.create_response(
                    ErrorObject, HTTPStatus.FORBIDDEN, 'Token has been revoked'
                )
            else:
                return fn(*args, **kwargs)
        else:
             return ErrorObject.create_response(
                 ErrorObject, HTTPStatus.FORBIDDEN, 'Unable to access this resource with provided token'
             )
    return wrapper
