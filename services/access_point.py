from models import AccessPoint
from playhouse.shortcuts import model_to_dict
from helpers.serializer import date_time_serializer
import json
from jsonpickle import encode


class AccessPointService():
    def get_all_access_points(self):
        for accessPoint in AccessPoint.select():
            print(accessPoint.description)
        """Return all the access point"""
        all_access_point_array = []

        for access_point in AccessPoint.select():
            all_access_point_array.append(model_to_dict(access_point))
        return json.dumps(all_access_point_array, default=date_time_serializer)

    def get_one_access_point(self, id):
        """Returns a single access point"""
        # return encode(model_to_dict(AccessPoint.get_by_id(id)),
        #               unpicklable=False,
        #               make_refs=False)
        return json.dumps(model_to_dict(AccessPoint.get_by_id(id)),
                      default=date_time_serializer)
