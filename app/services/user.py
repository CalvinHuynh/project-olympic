from datetime import datetime
from http import HTTPStatus

from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import dict_to_model, model_to_dict

from app.models import AccessPoint, User


class UserService():
    def get_user_by_id(self, id: int):
        """Get user by id

        Arguments:
            id {int} -- Id of user

        Raises:
            ValueError: User not found with given id

        Returns:
            User -- User object
        """
        try:
            return User.get_by_id(id)
        except DoesNotExist:
            raise ValueError('User with id {} does not exist'.format(id),
                             HTTPStatus.NOT_FOUND)
        # finally:
        #     return result

    def get_user_by_username(self, username: str):
        """Get user by username

        Arguments:
            username {str} -- Username
    
        Raises:
            ValueError: User not found with given username

        Returns:
            User -- User object
        """
        try:
            return model_to_dict(
                User.select().where(User.username == username).get())
        except DoesNotExist:
            raise ValueError(
                'User with username {} does not exist'.format(username),
                HTTPStatus.NOT_FOUND)
        except Exception:
            raise BaseException('Internal server error',
                                HTTPStatus.INTERNAL_SERVER_ERROR)

    def get_access_point_by_user(self, username: str):
        """Retrieves access point from an user
        
        Arguments:
            username {str} -- Username
        
        Returns:
            AccessPoint[] -- An array of access points
        """
        all_access_points_from_user_array = []
        try:
            try:
                user = dict_to_model(
                    User, UserService.get_user_by_username(self, username))
            except Exception:
                raise

            if user is not None:
                for access_point in AccessPoint.select(
                        AccessPoint, user).where(AccessPoint.user == user):
                    all_access_points_from_user_array.append(
                        model_to_dict(access_point))
            return all_access_points_from_user_array
        except Exception:
            raise

    def create_user(self, email: str, username=None):
        """Creates a new user
        
        Arguments:
            email {str} -- email of user
        
        Keyword Arguments:
            username {str} -- Optional: username of user (default: {None})
        
        Raises:
            ValueError: Email is required
            BaseException: Internal server error
        
        Returns:
            User -- Newly created user
        """
        join_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        last_login_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        try:
            return model_to_dict(
                User.create(username=username,
                            email=email,
                            join_date=join_date,
                            last_login_date=last_login_date))
        except IntegrityError:
            raise ValueError('Email is required', HTTPStatus.BAD_REQUEST)
        except Exception:
            raise BaseException('Internal server error',
                                HTTPStatus.INTERNAL_SERVER_ERROR)


def create_user_without_self(email: str, username=None):
        """Creates a new user
        
        Arguments:
            email {str} -- email of user
        
        Keyword Arguments:
            username {str} -- Optional: username of user (default: {None})
        
        Raises:
            ValueError: Email is required
            BaseException: Internal server error
        
        Returns:
            User -- Newly created user
        """
        join_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        last_login_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        try:
            return model_to_dict(
                User.create(username=username,
                            email=email,
                            join_date=join_date,
                            last_login_date=last_login_date))
        except IntegrityError:
            raise ValueError('Email is required', HTTPStatus.BAD_REQUEST)
        except Exception:
            raise BaseException('Internal server error',
                                HTTPStatus.INTERNAL_SERVER_ERROR)
