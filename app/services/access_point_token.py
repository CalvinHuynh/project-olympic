from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from http import HTTPStatus

from flask_jwt_extended import create_access_token
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict, dict_to_model

from app.dto import AccessPointDto
from app.models import AccessPoint, AccessPointToken, User

from .user import UserService
from .access_point import AccessPointService

user_service = UserService
access_point_service = AccessPointService


class AccessPointTokenService():
    def create_token_for_access_point(
            self,
            # access_point_dto: AccessPointDto,
            access_point_id: int,
            user_id: int):
        """Creates an jwt token
        
        Arguments:
            access_point_dto {AccessPointDto} -- [description]
            access_point_id {int} -- [description]
        
        Raises:
            ValueError: [description]
        
        Returns:
            [type] -- [description]
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
            expiry_date = (datetime.utcnow() + relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S')
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
            except Exception as err:
                print(err)
                raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR, 'Unable to create token for access point {}'.format(
                    access_point_id))
