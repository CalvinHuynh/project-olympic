from http import HTTPStatus

from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from app.dto import CreateAccessPointDto
from app.models import AccessPoint, User

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

    def get_access_point_by_id(self, id: int):
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
            raise ValueError(HTTPStatus.NOT_FOUND, 'Access point with id {} does not exist'.format(id))

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
                elif create_access_point_dto.user.username:
                    result = user_service.get_user_by_username(
                        self, create_access_point_dto.user.username)
                else:
                    print("Skipping as user has no fields")
                    pass
            elif user_id:
                result = user_service.get_user_by_id(self, user_id)
            else:
                result = user_service.get_user_by_username(self, username)
        except Exception:
            raise

        if result is not None and isinstance(result, User):
            try:
                return model_to_dict(
                    AccessPoint.create(
                        description=create_access_point_dto.description,
                        ip_addr=create_access_point_dto.ip_addr,
                        user=result))
            except Exception:
                raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR, "Unable to create access point")
