from http import HTTPStatus

from pandas import DataFrame, read_json, to_datetime
from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import model_to_dict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVR

import api.helpers.data_frame_helper as _df_helper
from api.helpers import (to_utc_datetime, validate_dateformat,
                         validate_string_bool, validate_string_int)
from api.models import CrowdForecast

from .data_source_data import DataSourceDataService as _DataSourceDataService

_label_encoder = LabelEncoder()


def _transform_data_to_dataframe(data):
    data_frame = DataFrame(data)
    # flooring the seconds
    data_frame['created_date'] = data_frame['created_date'].map(
        lambda x: x.replace(second=0))
    # Subtract the 8 devices/clients that are always connected, it needs to be
    # a variable instead of a static constant.
    # Since the number of always connected clients may vary (for example since
    # december there are only 7 always connected clients)
    data_frame['no_of_clients'] = data_frame['no_of_clients'] - 8
    data_frame.loc[data_frame['no_of_clients'] < 0, 'no_of_clients'] = 0
    return data_frame


def _add_time_characteristics(data_frame, time_unit: str = '1H'):
    data_frame = data_frame.resample(
        time_unit, on='created_date').mean().reset_index()
    data_frame['day_of_week'] = data_frame['created_date'].dt.dayofweek
    data_frame['date_hour'] = data_frame['created_date'].dt.hour
    data_frame['no_of_clients'].round(2)
    data_frame['is_weekend'] = data_frame['day_of_week'].apply(
        lambda x: _df_helper.item_in_list(x, [5, 6])
    )
    del data_frame['id']
    del data_frame['data_source']
    data_frame['is_weekend'] = _label_encoder.fit_transform(
        data_frame['is_weekend'])
    return data_frame


def _create_next_week_dataframe(start_date=None, day_of_week: int = 0):
    next_week_dataframe = DataFrame(
        {'created_date': _df_helper.get_future_timestamps(
            start_date, day_of_week)})
    next_week_dataframe['created_date'] = to_datetime(
        next_week_dataframe['created_date'], unit='s')
    next_week_dataframe['day_of_week'] = next_week_dataframe[
        'created_date'].dt.dayofweek
    next_week_dataframe['date_hour'] = next_week_dataframe[
        'created_date'].dt.hour
    next_week_dataframe['is_weekend'] = next_week_dataframe[
        'day_of_week'].apply(
        lambda x: _df_helper.item_in_list(x, [5, 6])
    )

    next_week_dataframe['is_weekend'] = _label_encoder.fit_transform(
        next_week_dataframe['is_weekend'])
    return next_week_dataframe


class ForecastService():
    def create_next_week_prediction(
            self,
            start_date=None,
            number_of_weeks_to_use: int = 4,
            use_start_of_the_week: bool = True):
        """Create next week prediction

        Keyword Arguments:
            start_date -- start_date is the starting point to get the data
             of the past week and to calculate the following week.
             (default : {None})
            number_of_weeks_to_use {int} -- number of weeks to use as input
            data (default: {3})
            use_start_of_the_week {bool} -- boolean to use the start of the
            week (default: {True})

        Returns:
            CrowdForecast -- A crowd forecast object will be returned
        """
        # retrieve the last three weeks for prediction
        # This service should run every saturday to get the forecast of the
        # following week
        import datetime as dt
        if start_date:
            validate_dateformat('start_date', start_date)
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()

        if not number_of_weeks_to_use:
            number_of_weeks_to_use = 4

        if not use_start_of_the_week:
            use_start_of_the_week = True

        try:
            use_start_of_the_week = validate_string_bool(use_start_of_the_week)
        except ValueError as err:
            raise ValueError(HTTPStatus.BAD_REQUEST, str(err))

        try:
            if not use_start_of_the_week:
                week_day = dt.date.today().weekday()
            else:
                week_day = 0  # let day of the week start at 0
            start, end = _df_helper.get_past_weeks(
                start_date=start_date,
                number_of_weeks=validate_string_int(number_of_weeks_to_use),
                use_start_of_the_week=use_start_of_the_week)
            data = _DataSourceDataService.get_all_data_from_data_source(
                _DataSourceDataService,
                data_source_id=2,
                limit=10000,
                start_date=start,
                end_date=end
            )

            data_frame = _transform_data_to_dataframe(data)
            data_frame = _add_time_characteristics(data_frame)
            # Drop rows where no_of_clients is NaN
            data_frame = data_frame.dropna(subset=['no_of_clients'])
            next_week_dataframe = _create_next_week_dataframe(
                start_date, week_day)
            next_week_start = dt.datetime.fromtimestamp(
                next_week_dataframe.iloc[[0]]['created_date']
                .values[0].astype(int) // 10**9)
            next_week_end = dt.datetime.fromtimestamp(
                next_week_dataframe.iloc[[-1]]['created_date']
                .values[0].astype(int) // 10**9)
            train, test = train_test_split(
                data_frame, test_size=0.25, shuffle=False)
            scaler = StandardScaler()
            train_X_scaled = scaler.fit_transform(train.iloc[:, range(2, 5)])
            train_y = train.iloc[:, 1]

            future_X_scaled = scaler.fit_transform(
                next_week_dataframe.iloc[:, range(1, 4)])

            svr_rbf = SVR(C=100.0, cache_size=200, coef0=0.0, degree=3,
                          epsilon=0.1, gamma=1.0, kernel='rbf', max_iter=-1,
                          shrinking=True, tol=0.001, verbose=False)
            result = svr_rbf.fit(
                train_X_scaled, train_y).predict(future_X_scaled)
            next_week_dataframe['predicted_no_of_clients'] = result
            result = CrowdForecast.create(
                created_date=to_utc_datetime(),
                date_range_used=f"{start}_{end}",
                number_of_weeks_used=number_of_weeks_to_use,
                prediction_for_week_nr=next_week_start.isocalendar()[1],
                prediction_start_date=next_week_start.strftime('%Y-%m-%d'),
                prediction_end_date=next_week_end.strftime('%Y-%m-%d'),
                prediction_data=next_week_dataframe.to_json()
            )
            return model_to_dict(result)
        except IntegrityError as err:
            print(err)  # replace with a logger
            raise ValueError(HTTPStatus.CONFLICT,
                             f"A forecast already exists with parameters:"
                             f"date_range_used: from {start} - {end} "
                             f"prediction_for_date: from "
                             f"{next_week_start.strftime('%Y-%m-%d')} - "
                             f"{next_week_end.strftime('%Y-%m-%d')}")
        except Exception as err:
            print(err)  # replace with a logger
            raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR,
                             "Internal error has occured.")

    def get_crowd_forecast(
            self,
            start_date: str,
            end_date: str,
            return_data_frame: bool = False):
        """Get crowd forecast for given dates

        Arguments:
            start_date {str} -- start date of prediction, accepted
            format '%Y-%m-%d'
            end_date {str} -- end date of prediction, accepted
            format '%Y-%m-%d'

        Keyword Arguments:
            return_data_frame {bool} -- If True, returns a jsonified
            dataframe (default: {False})
        """
        if not return_data_frame:
            return_data_frame = False
        try:
            validate_dateformat("start_date", start_date)
            validate_dateformat("end_date", end_date)
        except ValueError as err:
            raise ValueError(HTTPStatus.BAD_REQUEST, str(err))

        try:
            return_data_frame_bool = validate_string_bool(return_data_frame)
        except ValueError as err:
            raise ValueError(HTTPStatus.BAD_REQUEST, str(err))

        try:
            result = CrowdForecast.select().where(
                CrowdForecast.prediction_start_date == start_date,
                CrowdForecast.prediction_end_date == end_date).order_by(
                CrowdForecast.id.desc()).get()
            if return_data_frame_bool:
                dataframe = read_json(result.prediction_data)
                dataframe['created_date'] = to_datetime(
                    dataframe['created_date'], unit='ms')
                return(dataframe.to_json())
            else:
                return model_to_dict(result)
        except DoesNotExist as err:
            print(err)
            raise ValueError(HTTPStatus.NOT_FOUND,
                             "Unable to find forecast for given dates.")
        except Exception as err:
            print(err)
            raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR,
                             "Internal error has occured.")
