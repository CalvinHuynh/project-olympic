from http import HTTPStatus

from peewee import DoesNotExist

from models import User


class UserService():
    def get_user_by_id(self, id: int):
        """Retrieves the user by id

        Arguments:
            id {int} -- Id of user

        Returns:
            json -- Returns the user if found
        """
        try:
            return User.get_by_id(id)
        except DoesNotExist:
            raise ValueError('User with id {} does not exist'.format(id),
                             HTTPStatus.NOT_FOUND)
        # finally:
        #     return result

    def get_user_by_username(self, username: str):
        """Retrieves the user by username
        
        Arguments:
            username {str} -- Username of user
        
        Returns:
            json -- Returns the user if found
        """
        try:
            return User.select().where(User.username == username).get()
        except DoesNotExist:
            raise ValueError(
                'User with username {} does not exist'.format(username),
                HTTPStatus.NOT_FOUND)
