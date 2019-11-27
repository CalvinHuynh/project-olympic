from pandas import DataFrame, Series


def filter_json(expression: str, json_data: object):
    """Filters json data using JMESPath

    Arguments:
        expression {str} -- filter query
        json_data {object} -- json data to filter

    Returns:
        json -- filtered json data
    """
    from jmespath import search
    from json import dumps, loads
    try:
        return search(expression, loads(json_data))
    except Exception:
        data = dumps(json_data)
        return search(expression, loads(data))


def filter_column_json_data(data_frame: DataFrame, column_to_filter: str,
                            expression: str):
    """Filter all the json data of the data frame using JMESPath

    Arguments:
        data_frame {DataFrame} -- input dataframe
        column_to_filter {str} -- column to filter
        expression {str} -- filter query
    """
    for index in range(len(data_frame)):
        data_frame[column_to_filter].values[index] = filter_json(
            expression, data_frame[column_to_filter].values[index])
    return data_frame


def flatten_json_data_in_column(data_frame: DataFrame,
                                column_to_flatten: str,
                                range_to_flatten: int = None,
                                custom_prefix: str = None):
    """Flattens the json of a specific column of the given dataframe

    Arguments:
        data_frame {DataFrame} -- input dataframe
        column_to_flatten {str} -- column to flatten

    Keyword Arguments:
        range_to_flatten {int} -- able to flatten multiple columns that uses an
         index as identifier (default: None)
        custom_prefix {str} -- custom prefix for the flattened output
         (default: column)

    Returns:
        data_frame -- modified dataframe
    """
    from pandas.io.json import json_normalize

    prefix = None
    if custom_prefix:
        prefix = custom_prefix
    else:
        prefix = f'{column_to_flatten}_'

    if range_to_flatten:
        prefix = f'{column_to_flatten}_'
        for index in range(range_to_flatten):
            try:
                data_frame = data_frame.join(
                    json_normalize(data_frame[column_to_flatten + "_" +
                                              str(index)].tolist()).
                    add_prefix(prefix + str(index) + "_")).drop(
                        [column_to_flatten + "_" + str(index)], axis=1)
            except BaseException:
                pass
    else:
        data_frame = data_frame.join(
            json_normalize(data_frame[column_to_flatten].tolist()).add_prefix(
                prefix)).drop([column_to_flatten], axis=1)

    return data_frame


def unpack_json_array(data_frame: DataFrame, column_to_unpack: str):
    """Unpack json data of a specific column in the dataframe

    Arguments:
        data_frame {DataFrame} -- input dataframe
        column_to_unpack {str} -- column to unpack the json array from

    Returns:
        data_frame -- modified dataframe
    """
    return data_frame[column_to_unpack].apply(Series).merge(
        data_frame, left_index=True, right_index=True).drop([column_to_unpack],
                                                            axis=1)


def _rename_columns(col_name):
    if isinstance(col_name, int):
        return f'data_{col_name}'
    else:
        pass
    return col_name


def cached_dataframe_outdated(filename: str, time_unit: str, time_int: int):
    """Check if the cached .pkl dataframe is outdated

    Arguments:
        filename {str} -- filename of the .pkl dataframe
        time_unit {str} -- time units, e.g. hours, minutes, seconds
        time_int {int} -- number in int, this will be used in combination with
        time_unit. The resulting parameter would be for example: hours=1

    Returns:
        bool -- Returns True if the cache's timedelta exceeds the threshold.
    """
    import os
    import datetime
    import time

    cache_threshold = datetime.timedelta(**{time_unit: time_int})
    file_modify_time = None
    try:
        file_modify_time = os.path.getmtime(filename)
    except BaseException:
        file_modify_time = time.time()
        pass
    now = time.time()
    delta = datetime.timedelta(seconds=now - file_modify_time)
    if delta > cache_threshold:
        return True
    else:
        return False
