from datetime import datetime
from http import HTTPStatus

from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import dict_to_model, model_to_dict

from api.dto import CreateDataSourceDataDto
from api.helpers import to_utc_datetime
from api.models import DataSource, DataSourceData

from .data_source import DataSourceService as _DataSourceService

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
            raise ValueError(HTTPStatus.NOT_FOUND, 'Data with id {} does not exist'.format(id))

    def get_all_data(self):
        """Retrieves all data
        
        Returns:
            DataSourceData -- An array of all data source data will be returned
        """
        all_data_array = []

        for data in DataSourceData.select():
            all_data_array.append(model_to_dict(data))

        return all_data_array

    def post_access_point_data(self, access_point_id: int, create_data_source_data_dto: CreateDataSourceDataDto):
        """Creates a data point
        
        Arguments:
            access_point_id {int} -- id of access point
            create_data_source_data_dto {CreateDataSourceDataDto} -- Data transfer object
            containing the payload for the data point
        
        Raises:
            ValueError: Access point not found with given id
        
        Returns:
            DataSourceData -- DataSourceData object
        """
        data_source = None
        try:
            data_source = _data_source_service.get_access_point_by_id(
                self, access_point_id)
        except Exception:
            raise


        try:
            if create_data_source_data_dto:
                return model_to_dict(
                    DataSourceData.create(
                        data_source=dict_to_model(DataSource, data_source),
                        no_of_clients=create_data_source_data_dto.no_of_clients,
                        creation_date=to_utc_datetime()
                    )
                )
            else:
                raise ValueError(HTTPStatus.BAD_REQUEST, 'Body is required')
        except IntegrityError:
            raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR,
                             'Internal server error')
