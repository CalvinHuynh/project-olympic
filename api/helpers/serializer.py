import json
from collections import namedtuple
from datetime import date, datetime


def date_time_serializer(obj):
    """Serializes date and datetimes in json

    Arguments:
        obj {[type]} -- [description]

    Raises:
        TypeError: [description]

    Returns:
        [type] -- [description]
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def to_iso8601_datetime(when: str = 'now', obj_to_convert: datetime = None):
    """Converts Python's datetime object to comply with ISO 8601 specification
    
    Keyword Arguments:
        when {str} -- Returns the current UTC time in ISO 8601 compliant format (default: {'Now'})
        obj_to_convert {datetime} -- Converts given object to ISO 8601 compliant format [description] (default: {None})
    
    Returns:
        [type] -- [description]
    """
    if when and when.lower == 'now':
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    elif isinstance(obj_to_convert, datetime):
        return obj_to_convert.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    else:
        raise ValueError(
            "When parameter can only accept the keyword 'now' or given datetime object is not of type datetime")


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
