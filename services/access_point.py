import json
from http import HTTPStatus

from flask import jsonify
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from dto import CreateAccessPointDto
from helpers import ErrorObject, SuccessObject
from models import AccessPoint

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
        return jsonify(
            SuccessObject.create_response(self, HTTPStatus.OK,
                                          all_access_point_array))

    def get_one_access_point(self, id: int):
        """Retrieves a single access point
        
        Arguments:
            id {int} -- id of access point
        
        Returns:
            json -- If the access point exist, an access point will be returned. 
            Else a corresponding error will be returned
        """
        result = None
        try:
            result = SuccessObject.create_response(
                self, HTTPStatus.OK, model_to_dict(AccessPoint.get_by_id(id)))
        except DoesNotExist:
            result = ErrorObject.create_response(
                self, HTTPStatus.NOT_FOUND,
                ('Access point with id {} does not exist'.format(id)))
        finally:
            return jsonify(result)

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
        result = None
        user = None
          # try to lookup the user
        try:
            if create_access_point_dto.user:
                if create_access_point_dto.user.identifier:
                    user = user_service.get_user_by_id(
                        self, create_access_point_dto.user.identifier)
                else:
                    user = user_service.get_user_by_username(
                        self, create_access_point_dto.user.username)
            elif user_id:
                user = user_service.get_user_by_id(self, user_id)
            else:
                user = user_service.get_user_by_username(self, username)
        except:
            result = ErrorObject.create_response(
                self, HTTPStatus.BAD_REQUEST,
                "Unable to find user")

        if user is not None:
            try:
                AccessPoint.create(description=create_access_point_dto.description,User=user)
                result = SuccessObject.create_response(
                    self, HTTPStatus.CREATED, "Created access point")
            except:
                result = ErrorObject.create_response(
                    self, HTTPStatus.BAD_REQUEST, "Unable to create access point")

        else:        
            return result