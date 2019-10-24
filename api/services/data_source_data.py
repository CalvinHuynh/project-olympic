from http import HTTPStatus

from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import dict_to_model, model_to_dict

from api.dto import CreateDataSourceDataDto
from api.helpers import to_utc_datetime
from api.models import DataSource, DataSourceData

from .data_source import DataSourceService as _DataSourceService

_ALLOWED_ORDER_BY_VALUES = ['asc', 'desc']
_data_source_service = _DataSourceService


class DataSourceDataService():
    def get_one_data_point(self, id: int):
        """Retrieves a single data point

        Arguments:
            id {int} -- Id of data point

        Raises:
            ValueError: Data point not found with given id

        Returns:
            DataSourceData -- An data source data object will be returned
        """
        try:
            return model_to_dict(DataSourceData.get_by_id(id))
        except DoesNotExist:
            raise ValueError(HTTPStatus.NOT_FOUND,
                             'Data with id {} does not exist'.format(id))

    def get_all_data(self, limit: int = 20, order_by: str = 'desc'):
        """Retrieves all data

        Returns:
            DataSourceData -- An array of all data source data will be returned
        """
        all_data_array = []

        query = DataSourceData.select()

        # Build the query based on the query params
        if order_by.lower() in _ALLOWED_ORDER_BY_VALUES:
            if order_by.lower() == _ALLOWED_ORDER_BY_VALUES[0]:
                query = query.order_by(DataSourceData.id.asc())
            else:
                query = query.order_by(DataSourceData.id.desc())
        else:
            raise ValueError(
                HTTPStatus.BAD_REQUEST,
                'Invalid order_by value, only "asc" or "desc" are allowed')
        try:
            casted_limit = int(limit)
        except ValueError:
            raise ValueError(
                HTTPStatus.BAD_REQUEST,
                'Invalid limit value, only values of type <int> are allowed')

        query = query.limit(casted_limit)

        for data in query:
            all_data_array.append(model_to_dict(data))

        return all_data_array

    def post_data(self, data_source_id: int,
                  create_data_source_data_dto: CreateDataSourceDataDto):
        """Creates a data point

        Arguments:
            data_source_id {int} -- id of data source
            create_data_source_data_dto {CreateDataSourceDataDto} --
            Data transfer object
            containing the payload for the data point

        Raises:
            ValueError: Data source not found with given id

        Returns:
            DataSourceData -- DataSourceData object
        """
        data_source = None
        try:
            data_source = _data_source_service.get_data_source_by_id(
                self, data_source_id)
        except Exception:
            raise

        try:
            if create_data_source_data_dto:
                return model_to_dict(
                    DataSourceData.create(
                        data_source=dict_to_model(DataSource, data_source),
                        no_of_clients=create_data_source_data_dto.
                        no_of_clients,
                        creation_date=to_utc_datetime()))
            else:
                raise ValueError(HTTPStatus.BAD_REQUEST, 'Body is required')
        except IntegrityError:
            raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR,
                             'Internal server error')
