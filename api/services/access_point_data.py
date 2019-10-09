from datetime import datetime
from http import HTTPStatus

from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import dict_to_model, model_to_dict

from api.dto import CreateAccessPointDataDto
from api.helpers import to_utc_datetime
from api.models import AccessPoint, AccessPointData

from .access_point import AccessPointService

access_point_service = AccessPointService


class AccessPointDataService():
    def get_one_data_point(self, id: int):
        """Retrieves a single data point
        
        Arguments:
            id {int} -- Id of data point
        
        Raises:
            ValueError: Data point not found with given id
        
        Returns:
            AccessPointData -- An access point data object will be returned
        """
        try:
            return model_to_dict(AccessPointData.get_by_id(id))
        except DoesNotExist:
            raise ValueError(HTTPStatus.NOT_FOUND, 'Data with id {} does not exist'.format(id))

    def get_all_data(self):
        """Retrieves all data
        
        Returns:
            AccessPointData -- An array of all access point data will be returned
        """
        all_data_array = []

        for data in AccessPointData.select():
            all_data_array.append(model_to_dict(data))

        return all_data_array

    def post_access_point_data(self, access_point_id: int, create_access_point_data_dto: CreateAccessPointDataDto):
        """Creates a data point
        
        Arguments:
            access_point_id {int} -- id of access point
            create_access_point_data_dto {CreateAccessPointDataDto} -- Data transfer object
            containing the payload for the data point
        
        Raises:
            ValueError: Access point not found with given id
        
        Returns:
            AccessPointData -- AccessPointdata object
        """
        access_point = None
        try:
            access_point = access_point_service.get_access_point_by_id(
                self, access_point_id)
        except Exception:
            raise


        try:
            if create_access_point_data_dto:
                return model_to_dict(
                    AccessPointData.create(
                        access_point=dict_to_model(AccessPoint, access_point),
                        no_of_clients=create_access_point_data_dto.no_of_clients,
                        creation_date=to_utc_datetime()
                    )
                )
            else:
                raise ValueError(HTTPStatus.BAD_REQUEST, 'Body is required')
        except IntegrityError:
            raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR,
                             'Internal server error')
