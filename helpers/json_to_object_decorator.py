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


def _json_object_hook(name, data):
    return namedtuple(name, data.keys())(*data.values())


def convert_input_to_tuple(name):
    def wrapper():
        data = request.get_json()
        try: 
            return json.loads(data, object_hook=_json_object_hook(name, data))
        except ValueError:
            print("Trying to fix json structure")
            data = json.dumps(data)
            return json.loads(data, object_hook=_json_object_hook)
    return wrapper
