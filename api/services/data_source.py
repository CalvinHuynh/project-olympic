from http import HTTPStatus

from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from api.dto import CreateDataSourceDto
from api.models import DataSource, User

from .user import UserService as _UserService

_user_service = _UserService


class DataSourceService():
    def get_all_data_sources(self):
        """Retrieves all the data sources

        Returns:
            DataSource -- An array of data sources will be returned
        """
        all_data_source_array = []

        for data_source in DataSource.select():
            all_data_source_array.append(model_to_dict(data_source))

        return all_data_source_array

    def get_data_source_by_id(self, id: int):
        """Retrieves a single data source

        Arguments:
            id {int} -- Id of data source

        Raises:
            ValueError: Data source not found with given id

        Returns:
            DataSource -- An data source will be returned
        """
        try:
            return model_to_dict(DataSource.get_by_id(id))
        except DoesNotExist:
            raise ValueError(
                HTTPStatus.NOT_FOUND,
                'Data source with id {} does not exist'.format(id))

    def add_data_source(self,
                        create_data_source_dto: CreateDataSourceDto,
                        user_id=None,
                        username=None):
        """Creates a new data source

        Arguments:
            create_data_source_dto {CreateDataSourceDto} -- Data transfer
            object containing the description of the data source and user

        Keyword Arguments:
            user_id {int} -- Optional: id of user (default: {None})
            username {str} -- Optional: username of user (default: {None})
        """
        result = None
        # try to lookup the user
        try:
            if create_data_source_dto.user:
                if create_data_source_dto.user.id:
                    result = _user_service.get_user_by_id(
                        self, create_data_source_dto.user.id)
                elif create_data_source_dto.user.username:
                    result = _user_service.get_user_by_username(
                        self, create_data_source_dto.user.username)
                else:
                    print("Skipping as user has no fields")
                    pass
            elif user_id:
                result = _user_service.get_user_by_id(self, user_id)
            else:
                result = _user_service.get_user_by_username(self, username)
        except Exception:
            raise

        if result is not None and isinstance(result, User):
            try:
                return model_to_dict(
                    DataSource.create(
                        description=create_data_source_dto.description,
                        source=create_data_source_dto.source,
                        user=result))
            except Exception:
                raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR,
                                 "Unable to create data source")
