from http import HTTPStatus

from flask_jwt_extended import jwt_manager as jwt
from .object_helper import ErrorObject


from api.app import jwt

@jwt.expired_token_loader
def custom_expired_token_loader(self, token):
    token_type = token['type']
    return ErrorObject.create_response(
        self, HTTPStatus.UNAUTHORIZED,
        'The {} token has expired'.format(token_type))

@jwt.unauthorized_loader
def custom_unauthorized_loader(self):
    return ErrorObject.create_response(self, HTTPStatus.UNAUTHORIZED,
                                        'No access token provided')
