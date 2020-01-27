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


def to_utc_datetime(obj_to_convert: datetime = None):
    """Formats pythons datetime object to YYYY-mm-dd HH:MM:SS format

    Keyword Arguments:
        obj_to_convert {datetime} -- datetime object to convert
        (default: {None})

    Returns:
        datetime -- datetime object in the format YYYY-mm-dd HH:MM:SS
    """
    if obj_to_convert:
        return obj_to_convert.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def to_rfc3339_datetime(when: str = 'now', obj_to_convert: datetime = None):
    """Converts Python's datetime object to comply with RFC 3339 specification

    Keyword Arguments:
        when {str} -- Returns the current UTC time in RFC 3339 compliant
        format (default: {'Now'})
        obj_to_convert {datetime} -- Converts given object to RFC 3339
        compliant format [description] (default: {None})

    Returns:
        datetime -- datetime object in the following format
        YYYY-mm-ddTHH:MM:sssZ
    """
    if when and when.lower() == 'now':
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    elif isinstance(obj_to_convert, datetime) and obj_to_convert:
        return obj_to_convert.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    else:
        raise ValueError(
            "When parameter can only accept the keyword 'now' or given \
                datetime object is not of type datetime"
        )


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


def filter_items_from_list(txt_list: list, rgx_match: str):
    """Filter items matching regex

    Arguments:
        txt_list {list} -- list to filter
        rgx_match {str} -- regex to look for

    Returns:
        list -- a list containing the non matching items
    """
    import re
    filtered_list = []
    for item in txt_list:
        if not re.search(rgx_match, item):
            filtered_list.append(item)

    return filtered_list
