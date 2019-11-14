from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from .response_helper import ErrorObject


def _token_usage_counter_add(token_id: int):
    from api.services.data_source_token import DataSourceTokenService
    DataSourceTokenService.update_hit_count_and_date(DataSourceTokenService,
                                                     token_id)


def jwt_required_extended(fn):
    """
    A custom decorator that extends the functionality of the jwt_required
    function from the package flask_jwt_extended
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except IndexError:
            return ErrorObject.create_response(
                ErrorObject, HTTPStatus.UNAUTHORIZED,
                'No token provided in the format of "Bearer <JWT>"')
        token = get_jwt_identity()
        if token['is_user_token'] is False:
            from api.services.data_source_token import \
                DataSourceTokenService
            _token_usage_counter_add(token['data_source_token']['id'])
            if not DataSourceTokenService.check_if_token_is_active(
                    DataSourceTokenService, token['data_source_token']['id']):
                return ErrorObject.create_response(ErrorObject,
                                                   HTTPStatus.FORBIDDEN,
                                                   'Token has been revoked')
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
                ErrorObject, HTTPStatus.FORBIDDEN,
                'Unable to access this resource with provided token')
        else:
            return fn(*args, **kwargs)

    return wrapper


def check_for(argument: str):
    """A decorator that allows the user to set what type of token to check for.
    If the provided argument equals 'machine'. The decorator will check if the
    token is a machine token (this means that the field 'is_user_token' must
    be false). If it is a machine token, the decorator will check if it is
    active.

    Arguments:
        argument {str} -- type of token to check, accepted values are 'machine'
        or 'user'

    Raises:
        ValueError: Unsupported argument provided
    """
    def check(fn):
        """
        A wrapper that checks if the provided JWT is an user token.
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            token = get_jwt_identity()
            if argument.lower() == 'machine':
                if token['is_user_token'] is False:
                    from api.services.data_source_token import \
                        DataSourceTokenService
                    _token_usage_counter_add(token['data_source_token']['id'])
                    if DataSourceTokenService.check_if_token_is_active(
                            DataSourceTokenService,
                            token['data_source_token']['id']) is False:
                        return ErrorObject.create_response(
                            ErrorObject, HTTPStatus.FORBIDDEN,
                            'Token has been revoked')
                    else:
                        return fn(*args, **kwargs)
                else:
                    return ErrorObject.create_response(
                        ErrorObject, HTTPStatus.FORBIDDEN,
                        'Unable to access this resource with provided token')
            elif argument.lower() == 'user':
                if token['is_user_token'] is False:
                    _token_usage_counter_add(token['data_source_token']['id'])
                    return ErrorObject.create_response(
                        ErrorObject, HTTPStatus.FORBIDDEN,
                        'Unable to access this resource with provided token')
                else:
                    return fn(*args, **kwargs)
            else:
                raise ValueError('Unsupported argument provided')

        return wrapper

    return check
