from http import HTTPStatus

from flask import jsonify
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from helpers import ErrorObject, SuccessObject
from models import User


class UserService():
    def get_user_by_id(self, id: int):
        """Retrieves the user by id
        
        Arguments:
            id {int} -- Id of user
        
        Returns:
            json -- Returns the user if found
        """
        result = None
        try:
            result = SuccessObject.create_response(
                self, HTTPStatus.OK, model_to_dict(User.get_by_id(id)))
        except DoesNotExist:
            result = ErrorObject.create_response(
                self, HTTPStatus.NOT_FOUND,
                ('User with id {} does not exist'.format(id)))
        finally:
            return jsonify(result)

    def get_user_by_username(self, username: str):
        """Retrieves the user by username
        
        Arguments:
            username {str} -- Username of user
        
        Returns:
            json -- Returns the user if found
        """
        result = None
        try:
            result = SuccessObject.create_response(
                self, HTTPStatus.OK,
                model_to_dict(User.select().where(User.username == username)))
        except DoesNotExist:
            result = ErrorObject.create_response(
                self, HTTPStatus.NOT_FOUND,
                ('User with username {} does not exist'.format(username)))
        finally:
            return jsonify(result)
