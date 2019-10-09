from http import HTTPStatus

# from api.app import jwt
from api import app

jwt = app.jwt

# Overwrite default error handling
@jwt.invalid_token_loader
def custom_invalid_token_loader(self):
    from api.helpers import ErrorObject
    return ErrorObject.create_response(self, HTTPStatus.UNAUTHORIZED,
                                        'Invalid token provided')

@jwt.expired_token_loader
def custom_expired_token_loader(callback):
    from api.helpers import ErrorObject
    token_type = callback['type']
    return ErrorObject.create_response(
        ErrorObject, HTTPStatus.UNAUTHORIZED,
        'The {} token has expired'.format(token_type))

@jwt.unauthorized_loader
def custom_unauthorized_loader(self):
    from api.helpers import ErrorObject
    return ErrorObject.create_response(self, HTTPStatus.UNAUTHORIZED,
                                        'No access token provided')