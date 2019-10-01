from datetime import datetime
from http import HTTPStatus

from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import dict_to_model, model_to_dict

from app.models import AccessPoint, User, AccessPointToken


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
            raise ValueError(HTTPStatus.NOT_FOUND,
                             'User with id {} does not exist'.format(id))

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
            raise ValueError(HTTPStatus.NOT_FOUND, 'User with username {} does not exist'.format(username))
        except Exception:
            raise BaseException(HTTPStatus.INTERNAL_SERVER_ERROR, 'Internal server error')

    def get_user_by_email(self, email: str):
        """Get user by email
        
        Arguments:
            email {str} -- Email
        
        Raises:
            ValueError: User not found with given email
        
        Returns:
            User -- User object
        """
        try:
            return model_to_dict(
                User.select().where(User.email == email).get())
        except DoesNotExist:
            raise ValueError(HTTPStatus.NOT_FOUND, 'User with email {} does not exist'.format(email))
        except Exception:
            raise BaseException(HTTPStatus.INTERNAL_SERVER_ERROR, 'Internal server error')

    def get_access_point_by_user(self, username: str = None, id: int = None):
        """Retrieves access point from an user
        
        Arguments:
            username {str} -- (Optional) Username
            id {int} -- (Optional) Id of user
        
        Returns:
            AccessPoint[] -- An array of access points
        """
        all_access_points_from_user_array = []
        user = None
        try:
            try:
                if username is not None:
                    user = dict_to_model(
                        User, UserService.get_user_by_username(self, username))
                elif id is not None:
                    user = dict_to_model(
                        User, UserService.get_user_by_id(self, id)
                    )
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
            if username is not None:
                return model_to_dict(
                    User.create(
                        username=username,
                        email=email,
                        join_date=join_date,
                        last_login_date=last_login_date))
            else:
                return model_to_dict(
                    User.create(email=email,
                                join_date=join_date,
                                last_login_date=last_login_date))
        except IntegrityError:
            if email is None:
                raise ValueError(HTTPStatus.BAD_REQUEST, 'Email is required')
            else:
                raise ValueError(HTTPStatus.CONFLICT, 'Email already exists')
        except Exception:
            raise BaseException(HTTPStatus.INTERNAL_SERVER_ERROR, 'Internal server error')

    def set_username(self, id: int, username: str):
        """Sets the username of the logged in user
        
        Arguments:
            id {int} -- User id
            username {str} -- new username
        """
        user: User = UserService.get_user_by_id(self, id)
        if user is not None and username is not None:
            if user.username is None:
                user.username = username
                try:
                    user.save()
                    return model_to_dict(user)
                except:
                    raise ValueError(HTTPStatus.CONFLICT, 'Username already exists')
            else:
                raise ValueError(HTTPStatus.NOT_MODIFIED, 'Username can only be set once')
        else:
            raise ValueError(HTTPStatus.BAD_REQUEST, 'Username is required')

    def get_access_point_tokens_by_user(self, id: int):
        """Get access point tokens by user
        
        Arguments:
            id {int} -- User id
        
        Returns:
            AccessPointTokens[] -- An array of access point tokens objects
        """
        all_access_point_tokens_array = []
        user = None
        try:
            user: User = UserService.get_user_by_id(self, id)
        except Exception:
            raise
        
        try:
            if user is not None:
                for access_point_tokens in AccessPointToken.select(
                        AccessPointToken, user).where(AccessPointToken.user == user):
                    all_access_point_tokens_array.append(
                        model_to_dict(access_point_tokens))
            return all_access_point_tokens_array
        except Exception:
            raise