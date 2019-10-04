from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from http import HTTPStatus

from flask_jwt_extended import create_access_token
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict, dict_to_model

from api.dto import AccessPointDto
from api.models import AccessPoint, AccessPointToken, User

from .user import UserService
from .access_point import AccessPointService

user_service = UserService
access_point_service = AccessPointService


class AccessPointTokenService():
    def get_token_by_id(self, id: int):
        """Retrieves access point token by id
        
        Arguments:
            id {int} -- access point token id
        
        Raises:
            ValueError: Id does not exist
        
        Returns:
            AccessPointToken -- AccessPointToken object
        """
        try:
            return AccessPointToken.get_by_id(id)
        except DoesNotExist:
            raise ValueError(HTTPStatus.NOT_FOUND,
                             'Token with id {} does not exist'.format(id))

    def create_token_for_access_point(
            self,
            # access_point_dto: AccessPointDto,
            access_point_id: int,
            user_id: int):
        """Creates a JWT for an access point
        
        Arguments:
            access_point_id {int} -- Id of access point
            user_id {int} -- Id of user
        
        Raises:
            ValueError: Unable to create token for access point
        
        Returns:
            JWT -- Returns an JWT
        """
        user: User = None
        access_point: AccessPoint = None
        try:
            if user_id:
                user = user_service.get_user_by_id(
                    self, user_id)
        except Exception:
            raise

        try:
            if access_point_id:
                access_point = dict_to_model(
                    AccessPoint, access_point_service.get_access_point_by_id(self, access_point_id))
        except Exception:
            raise

        if user is not None and isinstance(user, User) and access_point is not None and isinstance(access_point, AccessPoint):
            created_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            last_activity_date = None
            # Set validity of token to 1 year
            expiry_date = (datetime.utcnow() + relativedelta(years=1)
                           ).strftime('%Y-%m-%d %H:%M:%S')
            no_of_usage = 0
            try:
                result = model_to_dict(
                    AccessPointToken.create(
                        user=user,
                        access_point=access_point,
                        created_date=created_date,
                        last_activity_date=last_activity_date,
                        expiry_date=expiry_date,
                        no_of_usage=no_of_usage,
                        is_active=True
                    )
                )
                identity_object = {
                    "is_user_token": False,
                    "access_point_token": result
                }
                return create_access_token(identity=identity_object, expires_delta=relativedelta(years=1))
            except Exception:
                raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR, 'Unable to create token for access point {}'.format(
                    access_point_id))

    def update_hit_count_and_date(self, access_point_token_id: int):
        """Update the hit counter of an access point token
        
        Arguments:
            access_point_token_id {int} -- Id of access point token
        
        Returns:
            AccessPointToken -- An updated AccessPointToken
        """
        access_point_token: AccessPointToken = AccessPointTokenService.get_token_by_id(self, access_point_token_id)
        if access_point_token is not None:
            access_point_token.no_of_usage += 1
            access_point_token.last_activity_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            access_point_token.save()
            return HTTPStatus.NO_CONTENT
        else:
            raise

    def check_if_token_is_active(self, access_point_token_id: int):
        """Check if token is active
        
        Arguments:
            access_point_token_id {int} -- Id of access token
        
        Returns:
            Bool -- [description]
        """
        access_point_token: AccessPointToken = AccessPointTokenService.get_token_by_id(self, access_point_token_id)
        if access_point_token is not None:
            if access_point_token.is_active:
                return True
            else:
                return False
        else:
            raise

    def revoke_token(self, access_point_token_id: int):
        """Revokes access token
        
        Arguments:
            access_point_token_id {int} -- Id of access token
        
        Returns:
            AccessPointToken -- Deactivated AccessPointToken object
        """
        access_point_token: AccessPointToken = AccessPointTokenService.get_token_by_id(self, access_point_token_id)
        if access_point_token is not None:
            access_point_token.is_active = False
            access_point_token.deactivated_since = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            access_point_token.save()
            return model_to_dict(access_point_token)
        else:
            raise