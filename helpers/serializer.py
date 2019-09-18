import json
from datetime import date, datetime


def date_time_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# class Object:
#     def to_json_serializer(self):
#         """Transforms an object to a dictionary to turn it to a json object"""

#         return json.dumps(self,
#                           default=lambda o: o.__dict__,
#                           sort_keys=True,
#                           indent=4)
