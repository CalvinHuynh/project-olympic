# WIP, should be a decorator that converts the payload dict object to a json object
import json

from collections import namedtuple
from flask import request


# from https://stackoverflow.com/a/30721433
def convert_input_to(class_):
    def wrap(f):
        def decorator(*args):
            obj = class_(**request.get_json())
            return f(obj)
        return decorator
    return wrap

# inspired by https://stackoverflow.com/a/15882054
def _json_object_hook(data):
    return namedtuple(type(data).__name__, data.keys())(*data.values())

"""Decorator that converts the API payload to an tuple object

Returns:
    namedtuple -- object representation of the API payload
"""
def convert_input_to_tuple(f):
        def decorator(*args, **kwargs):
            data = args[0].api.payload
            try: 
                kwargs['tupled_output'] = json.loads(data, object_hook=_json_object_hook)
                return f(*args, **kwargs)
            except Exception:
                data = json.dumps(data)
                kwargs['tupled_output'] = json.loads(data, object_hook=_json_object_hook)
                return f(*args, **kwargs)
        return decorator