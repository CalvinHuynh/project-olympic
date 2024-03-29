from http import HTTPStatus

from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import dict_to_model, model_to_dict

from api.helpers import add_extra_info_to_dict, to_utc_datetime
from api.models import DataSource, DataSourceToken, User


class UserService():
    def get_user_by_id(self, user_id: int, to_dict: bool = False):
        """Get user by user_id

        Arguments:
            user_id {int} -- Id of user

        Raises:
            ValueError: User not found with given user_id

        Returns:
            User -- User object
        """
        try:
            if to_dict:
                return model_to_dict(User.get_by_id(user_id))
            return User.get_by_id(user_id)
        except DoesNotExist:
            raise ValueError(HTTPStatus.NOT_FOUND,
                             'User with id {} does not exist'.format(user_id))

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
                HTTPStatus.NOT_FOUND,
                'User with username {} does not exist'.format(username))
        except Exception:
            raise BaseException(HTTPStatus.INTERNAL_SERVER_ERROR,
                                'Internal server error')

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
            raise ValueError(HTTPStatus.NOT_FOUND,
                             'User with email {} does not exist'.format(email))
        except Exception:
            raise BaseException(HTTPStatus.INTERNAL_SERVER_ERROR,
                                'Internal server error')

    def get_data_source_by_user(self, username: str = None, id: int = None):
        """Retrieves data source from an user

        Arguments:
            username {str} -- Optional Username
            id {int} -- Optional Id of user

        Returns:
            DataSource[] -- An array of data sources
        """
        all_data_sources_from_user_array = []
        user = None
        try:
            try:
                if username is not None:
                    user = dict_to_model(
                        User, UserService.get_user_by_username(self, username))
                elif id is not None:
                    user = dict_to_model(User,
                                         UserService.get_user_by_id(self, id))
            except Exception:
                raise

            if user is not None:
                for data_source in DataSource.select(
                        DataSource, user).where(DataSource.user == user):
                    all_data_sources_from_user_array.append(
                        model_to_dict(data_source))
            return all_data_sources_from_user_array
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
        join_date = to_utc_datetime()
        last_login_date = to_utc_datetime()
        try:
            if username is not None:
                return model_to_dict(
                    User.create(username=username,
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
            raise BaseException(HTTPStatus.INTERNAL_SERVER_ERROR,
                                'Internal server error')

    def set_username(self, user_id: int, username: str):
        """Sets the username of the logged in user

        Arguments:
            user_id {int} -- User id
            username {str} -- new username
        """
        user: User = UserService.get_user_by_id(self, user_id)
        if user is not None and username is not None:
            if user.username is None:
                user.username = username
                try:
                    user.save()
                    return model_to_dict(user)
                except BaseException:
                    raise ValueError(HTTPStatus.CONFLICT,
                                     'Username already exists')
            else:
                raise ValueError(HTTPStatus.NOT_MODIFIED,
                                 'Username can only be set once')
        else:
            raise ValueError(HTTPStatus.BAD_REQUEST, 'Username is required')

    def get_data_source_tokens_by_user(self, user_id: int):
        """Get data source tokens by user

        Arguments:
            user_id {int} -- User id

        Returns:
            DataSourceToken[] -- An array of data source tokens objects
        """
        all_data_source_tokens_array = []
        user = None
        try:
            user: User = UserService.get_user_by_id(self, user_id)
        except Exception:
            raise

        try:
            for data_source_token in DataSourceToken.select(
                    DataSourceToken,
                    user).where(DataSourceToken.user_id == user_id):
                all_data_source_tokens_array.append(
                    model_to_dict(data_source_token, recurse=False))
            return all_data_source_tokens_array
        except Exception:
            raise

    def deactivate_token_of_user(self, user_id: int,
                                 data_source_token_id: int):
        """Deactivates the token of the user

        Arguments:
            user_id {int} -- User id
            data_source_token_id {int} -- Token id

        Returns:
            DataSourceToken -- Deactivated DataSourceToken object
        """
        try:
            data_source_token = DataSourceToken.get(
                (DataSourceToken.id == data_source_token_id) &
                (DataSourceToken.user_id == user_id))
            if data_source_token.is_active:
                data_source_token.is_active = False
                data_source_token.deactivated_since = to_utc_datetime()
                data_source_token.save()
                return model_to_dict(data_source_token, recurse=False)
            else:
                return_dict = model_to_dict(data_source_token, recurse=False)
                return_dict = add_extra_info_to_dict(
                    return_dict, 'message',
                    f'Token with id {data_source_token_id} has already been '
                    f'deactivated.'
                )
                return return_dict
        except DoesNotExist:
            raise ValueError(
                HTTPStatus.NOT_FOUND,
                'Unable to find data source token given user and token id')
