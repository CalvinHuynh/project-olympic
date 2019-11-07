from api.settings import FLASK_API_VERSION

api_version = FLASK_API_VERSION if FLASK_API_VERSION else "1.0.0"


class ErrorObject:
    """An helper that creates the error response.

    Returns:
        ErrorObject -- Object containing the error with a message and a
        corresponding status code.
    """
    def create_response(self, error_code, error_message: str):
        return ({
            "apiVersion": api_version,
            "error": {
                "code": error_code,
                "message": error_message
            }
        }, error_code)


class SuccessObject:
    """An helper that creates a succesful response.

    Returns:
        SuccessObject -- Object containg the data when the response is
        successful.
    """
    def create_response(self,
                        status_code,
                        data: object,
                        return_count: bool = False):
        response = {"apiVersion": api_version, "data": data}

        if return_count:
            response['count'] = len(data)
        return response


def remove_items_from_dict(dictionary: dict, items_to_remove: list):
    """Helper to delete elements from a dictionary

    Arguments:
        dictionary {dict} -- Dictionary to mutate.
        items_to_remove {list} -- Keys to remove.

    Returns:
        dictionary -- Returns the mutated dictionary
    """
    for item in items_to_remove:
        del dictionary[item]

    return dictionary


def add_extra_info_to_dict(dictionary: dict,
                           key_name: str,
                           extra_information: object,
                           extra_fields_name: str = '_extra_fields'):
    """Adds extra information to the dictionary

    Arguments:
        dictionary {dict} -- dictionary to add the extra information to.
        key_name {str} -- name of key.
        extra_information {object} -- An object containing the extra\
             information.

    Keyword Arguments:
        extra_fields_name {str} -- the extra fields key name\
             (default: {'_extra_fields'})

    Returns:
        dictionary -- Returns the dictionary with the extra fields
    """
    if extra_fields_name not in dictionary:
        dictionary[extra_fields_name] = {}

    if key_name not in dictionary[extra_fields_name]:
        dictionary[extra_fields_name][key_name] = extra_information
    return dictionary
