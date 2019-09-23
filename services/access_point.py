import json
from http import HTTPStatus

from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from dto import CreateAccessPointDto
from helpers import json_to_object
from models import AccessPoint, User

from .user import UserService


user_service = UserService


class AccessPointService():
    def get_all_access_points(self):
        """Retrieves all the access points
        
        Returns:
            json -- Returns all the access points
        """
        all_access_point_array = []

        for access_point in AccessPoint.select():
            all_access_point_array.append(model_to_dict(access_point))

        return all_access_point_array

    def get_one_access_point(self, id: int):
        """Retrieves a single access point
        
        Arguments:
            id {int} -- id of access point
        
        Returns:
            json -- If the access point exist, an access point will be returned. 
            Else a corresponding error will be returned
        """
        try:
            return model_to_dict(AccessPoint.get_by_id(id))
        except DoesNotExist:
            raise ValueError(
                'Access point with id {} does not exist'.format(id),
                HTTPStatus.NOT_FOUND)

    def add_access_point(self,
                         create_access_point_dto: CreateAccessPointDto,
                         user_id=None,
                         username=None):
        """Creates a new access point
        
        Arguments:
            create_access_point_dto {CreateAccessPoint} -- Object containing the 
            user and a description for the access point.

            user_id {int} -- Optional: User id

            username {str} -- Optional: Username
        
        Returns:
            json -- If created, the new access point will be returned.
            Else a corresponding error will be returned
        """
        # Maps incomming dictionary to strongly typed object
        create_access_point_dto: CreateAccessPointDto = json_to_object(
            json.dumps(create_access_point_dto))

        result = None
        # try to lookup the user
        try:
            if create_access_point_dto.user:
                if create_access_point_dto.user.id:
                    result = user_service.get_user_by_id(
                        self, create_access_point_dto.user.id)
                else:
                    result = user_service.get_user_by_username(
                        self, create_access_point_dto.user.username)
            elif user_id:
                result = user_service.get_user_by_id(self, user_id)
            else:
                result = user_service.get_user_by_username(self, username)
        except Exception as err:
            raise ValueError(err.args[0], err.args[1])

        if result is not None and isinstance(result, User):
            try:
                return model_to_dict(
                    AccessPoint.create(
                        description=create_access_point_dto.description,
                        user=result))
            except:
                raise ValueError("Unable to create access point",
                                 HTTPStatus.INTERNAL_SERVER_ERROR)
