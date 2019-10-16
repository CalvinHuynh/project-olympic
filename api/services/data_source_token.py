from datetime import datetime
from http import HTTPStatus

from dateutil.relativedelta import relativedelta
from flask_jwt_extended import create_access_token
from peewee import DoesNotExist
from playhouse.shortcuts import dict_to_model, model_to_dict

from api.helpers import to_utc_datetime
from api.models import DataSource, DataSourceToken, User

from .data_source import DataSourceService as _DataSourceService
from .user import UserService as _UserService

_user_service = _UserService
_data_source_service = _DataSourceService


class DataSourceTokenService():
    def get_token_by_id(self, id: int):
        """Retrieves data source token by id

        Arguments:
            id {int} -- data source token id

        Raises:
            ValueError: Id does not exist

        Returns:
            DataSourceToken -- DataSourceToken object
        """
        try:
            return DataSourceToken.get_by_id(id)
        except DoesNotExist:
            raise ValueError(HTTPStatus.NOT_FOUND,
                             'Token with id {} does not exist'.format(id))

    def create_token_for_data_source(self, data_source_id: int, user_id: int):
        """Creates a JWT for an data source

        Arguments:
            data_source_id {int} -- Id of data source
            user_id {int} -- Id of user

        Raises:
            ValueError: Unable to create token for data source

        Returns:
            JWT -- Returns an JWT
        """
        user: User = None
        data_source: DataSource = None
        try:
            if user_id:
                user = _user_service.get_user_by_id(self, user_id)
        except Exception:
            raise

        try:
            if data_source_id:
                data_source = dict_to_model(
                    DataSource,
                    _data_source_service.get_data_source_by_id(
                        self, data_source_id))
        except Exception:
            raise

        if user is not None and isinstance(
                user, User) and data_source is not None and isinstance(
                    data_source, DataSource):
            created_date = to_utc_datetime()
            last_activity_date = None
            # Set validity of token to 1 year
            expiry_date = to_utc_datetime(
                (datetime.utcnow() + relativedelta(years=1)))
            no_of_usage = 0
            try:
                result = model_to_dict(
                    DataSourceToken.create(
                        user=user,
                        data_source=data_source,
                        created_date=created_date,
                        last_activity_date=last_activity_date,
                        expiry_date=expiry_date,
                        no_of_usage=no_of_usage,
                        is_active=True))
                identity_object = {
                    "is_user_token": False,
                    "data_source_token": result
                }
                return create_access_token(
                    identity=identity_object,
                    expires_delta=relativedelta(years=1))
            except Exception:
                raise ValueError(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    'Unable to create token for data source {}'.format(
                        data_source_id))

    def update_hit_count_and_date(self, data_source_token_id: int):
        """Update the hit counter of an data source token

        Arguments:
            data_source_token_id {int} -- Id of data source token

        Returns:
            HTTPstatus code -- 204 No Content
        """
        data_source_token = DataSourceTokenService.get_token_by_id(
            self, data_source_token_id)
        if data_source_token is not None:
            data_source_token.no_of_usage += 1
            data_source_token.last_activity_date = to_utc_datetime()
            data_source_token.save()
            return HTTPStatus.NO_CONTENT
        else:
            raise

    def check_if_token_is_active(self, data_source_token_id: int):
        """Check if token is active

        Arguments:
            data_source_token_id {int} -- Id of data source token

        Returns:
            Boolean -- True if token is active, else False
        """
        data_source_token = DataSourceTokenService.get_token_by_id(
            self, data_source_token_id)
        if data_source_token is not None:
            if data_source_token.is_active:
                return True
            else:
                return False
        else:
            raise

    def revoke_token(self, data_source_token_id: int):
        """Revokes token of data source

        Arguments:
            data_source_token_id {int} -- Id of data source token

        Returns:
            DataSourceToken -- Deactivated DataSourceToken object
        """
        data_source_token = DataSourceTokenService.get_token_by_id(
            self, data_source_token_id)
        if data_source_token is not None:
            data_source_token.is_active = False
            data_source_token.deactivated_since = to_utc_datetime()
            data_source_token.save()
            return model_to_dict(data_source_token)
        else:
            raise
