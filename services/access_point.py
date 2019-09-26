import json
from http import HTTPStatus

from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from dto import CreateAccessPointDto
from models import AccessPoint, User

from .user import UserService

user_service = UserService


class AccessPointService():
    def get_all_access_points(self):
        """Retrieves all the access points

        Returns:
            [AccessPoint] -- An array of access points will be returned
        """
        all_access_points_array = []

        for access_point in AccessPoint.select():
            all_access_points_array.append(model_to_dict(access_point))

        return all_access_points_array

    def get_one_access_point(self, id: int):
        """Retrieves a single access point

        Arguments:
            id {int} -- Id of access point

        Raises:
            ValueError: Access point not found with given id

        Returns:
            AccessPoint -- An access point will be returned
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
            create_access_point_dto {CreateAccessPointDto} -- Data transfer
            object containing the description of the access point and user

        Keyword Arguments:
            user_id {int} -- Optional: id of user (default: {None})
            username {str} -- Optional: username of user (default: {None})
        """
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
            except Exception:
                raise ValueError("Unable to create access point",
                                 HTTPStatus.INTERNAL_SERVER_ERROR)
