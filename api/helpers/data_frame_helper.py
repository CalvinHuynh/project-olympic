from numpy import int as np_int
from pandas import DataFrame, Series

from .validators import validate_dateformat


def filter_json(expression: str, json_data: object):
    """Filters json data using JMESPath

    Arguments:
        expression {str} -- filter query
        json_data {object} -- json data to filter

    Returns:
        json -- returns the filtered json data
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
        data_frame -- returns the modified dataframe
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
        data_frame -- returns a modified dataframe
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
        bool -- returns True if the cache's timedelta exceeds the threshold.
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


def drop_columns_with_postfix(df: DataFrame, postfix_to_drop: str = '_y'):
    """Function to drop common columns after a merge

    Arguments:
        df {DataFrame} -- dataframe to drop columns from

    Keyword Arguments:
        postfix_to_drop {str} -- postfix of column to drop (default: {'_y'})

    Returns:
        {DataFrame} -- returns a dataframe with the matching columns dropped
    """
    all_columns_in_df = list(df)
    for col in all_columns_in_df:
        if col.endswith(postfix_to_drop):
            del df[col]
    return df


def convert_list_to_string(list_to_join: list):
    """Converts a given list to a comma separated string.

    Arguments:
        list_to_join {list} -- list to convert

    Returns:
        {str} -- returns a joined together string
    """
    return ", ".join(list_to_join)


def item_in_list(item: str, item_list: list):
    """Check if a given item is in a given list.
    If the given item occurs in a list, an 1 will be returned.
    Else a 0 will be returned.

    Arguments:
        item {str} -- item to check
        item_list {list} -- list of items

    Returns:
        {int} -- returns an 1 if item is in list, else 0.
    """
    if item in item_list:
        return 1
    else:
        return 0


def strip_from_string(
        string_to_split: str,
        index: int = 2,
        strip_character: str = '_'):
    return strip_character.join(string_to_split.split(strip_character)[:index])


def _find_value_near_datetime(
        data_frame: DataFrame,
        column_name: str,
        value_to_find):
    idx = data_frame[column_name].sub(value_to_find).abs().idxmin()
    nearest_date = str(
        data_frame.loc[[idx]]['created_date'].values[0].astype(np_int) // 10**9
    )
    if (nearest_date > value_to_find.strftime('%s')):
        return data_frame.loc[[idx - 1]]
    else:
        return data_frame.loc[[idx]]


def fill_missing_values_using_forecast(
        missing_val_data_frame: DataFrame,
        forecast_data_frame: DataFrame,
        column_name: str):
    """
    Fill missing weather values using saved forecast data

    Arguments:
        missing_val_data_frame {DataFrame} -- data frame that contains missing
         weather values
        forecast_data_frame {DataFrame} -- data frame that contains the
         weather forecast, this data frame will be used to fill the missing
         weather values
        column_name {str} -- column name will be used to match the data frames
    Returns:
        {DataFrame} -- data frame that has been filled in using forecast data
    """
    for index, row in missing_val_data_frame.iterrows():
        forecast_row = _find_value_near_datetime(
            forecast_data_frame, column_name, row['created_date']
        )
        matching_col = forecast_row[forecast_row.columns[forecast_row.iloc[(
            0)] == row['created_date']]]
        if not matching_col.empty:
            col_prefix_to_match = strip_from_string(list(matching_col)[0])
            columns_to_fill = [
                '_main.temp', '_main.pressure', '_main.humidity',
                '_main.temp_min', '_main.temp_max', '_wind.speed',
                '_wind.deg', '_clouds.all', '_weather.main',
                '_weather.description', '_rain.3h', '_dt'
            ]
            for col_postfix in columns_to_fill:
                if col_postfix == '_dt':
                    missing_val_data_frame.loc[
                        index, f'data{col_postfix}'
                    ] = forecast_row[
                        f"{col_prefix_to_match}{col_postfix}"
                    ].values[0].astype(np_int) // 10**9
                else:
                    missing_val_data_frame.loc[
                        index, f'data{col_postfix}'
                    ] = forecast_row[
                        f"{col_prefix_to_match}{col_postfix}"].values[0]
    return missing_val_data_frame


def get_future_timestamps(
        start_date=None,
        day_of_week: int = 0,
        timestamp: int = 3600,
        number_of_timestamps: int = 167):
    """Calculates the future timestamps from a given day of the week.

    Keyword Arguments:
        start_date -- start_date to base the future timestamps from.
        If start_date is None, today is used (default : {None})
        day_of_week {int} -- calculate next day of the week
        (0-6, where 0 is monday and 6 is sunday)  (default: {0})
        timestamp {int} -- timestamp (default: {3600})
        number_of_timestamps {int} -- how many timestamps to calculate
        (default is 1 week worth of timestamps) (default: {168})

    Returns:
        [list] -- Returns a list containing one week worth of timestamps
    """
    import datetime as dt
    future_timestamps = []
    if not start_date:
        start_date = dt.date.today()
    else:
        validate_dateformat('start_date', start_date)
        if not isinstance(start_date, dt.date):
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    next_day_of_week = start_date + dt.timedelta(
        (day_of_week - start_date.weekday()) % 7)
    timestamp_next_day_of_week = int(
        (next_day_of_week - dt.date(1970, 1, 1)).total_seconds())

    accumulative_timestamp = 0
    for index in range(number_of_timestamps):
        future_timestamps.append(
            timestamp_next_day_of_week + accumulative_timestamp)
        accumulative_timestamp += timestamp
    return future_timestamps


def get_start_and_end_of_month():
    """Retrieves the last month

    Returns:
        dict -- Returns a dictionary containing the start date and end date of
        the previous month.
    """
    import datetime as dt
    from dateutil.relativedelta import relativedelta
    month_start = dt.date.today().replace(day=1)
    month_end = month_start + relativedelta(months=1) - dt.timedelta(days=1)
    return month_start, month_end


def get_past_weeks(
        start_date=None,
        number_of_weeks: int = 3,
        use_start_of_the_week: bool = True):
    """Retrieves the past weeks

    Keyword Arguments:
        number_of_weeks {int} -- number of weeks to substract from the current
        week (default: {3})
        use_start_of_the_week {bool} -- return weeks that starts on monday
        (default: {True})

    Returns:
        dict -- Returns a dictionary containing the start week and end week of
        the past.
    """
    import datetime as dt
    if not start_date:
        start_date = dt.date.today()
    else:
        validate_dateformat('start_date', start_date)
        if not isinstance(start_date, dt.date):
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    if use_start_of_the_week:
        start_week = start_date - dt.timedelta(
            days=start_date.weekday(), weeks=number_of_weeks)
        end_week = start_date - dt.timedelta(
            days=start_date.weekday())
    else:
        start_week = start_date - dt.timedelta(weeks=number_of_weeks)
        end_week = start_date

    return start_week, end_week
