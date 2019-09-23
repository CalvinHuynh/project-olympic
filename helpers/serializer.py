import json
from datetime import date, datetime
from collections import namedtuple

def date_time_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def _json_object_hook(d):
    return namedtuple(type(d).__name__, d.keys())(*d.values())


def json_to_object(data):
    """Converts Json to strongly typed object
    
    Arguments:
        data {JSON} -- data in valid json format
    
    Returns:
        dict -- a dictionary representation of the json
    """
    try: 
        return json.loads(data, object_hook=_json_object_hook)
    except ValueError:
        # print("Trying to fix json structure")
        data = json.dumps(data)
        return json.loads(data, object_hook=_json_object_hook)
    