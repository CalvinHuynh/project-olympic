import json

from flask import jsonify
from playhouse.shortcuts import model_to_dict
from peewee import DoesNotExist
from http import HTTPStatus

from helpers import SuccessObject, ErrorObject
from models import AccessPoint
from dto import CreateAccessPointDto


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

    def get_one_access_point(self, id):
        """Retrieves a single access point
        
        Arguments:
            id {integer} -- id of access point
        
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

    def add_access_point(self, create_access_point_dto: CreateAccessPointDto):
        """Creates a new access point
        
        Arguments:
            create_access_point_dto {CreateAccessPoint} -- Object containing the 
            user and a description for the access point.
        
        Returns:
            json -- If created, the new access point will be returned.
            Else a corresponding error will be returned
        """
        result = None
        try:
            result = SuccessObject.create_response(
                self, HTTPStatus.CREATED,
                AccessPoint.create(
                    description=create_access_point_dto.description,
                    User=create_access_point_dto.User))
        except:
            result = ErrorObject.create_response(
                self, HTTPStatus.BAD_REQUEST, "Unable to create access point")
        finally:
            return result
