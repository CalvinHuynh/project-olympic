from http import HTTPStatus

from pandas import DataFrame, to_datetime
# from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import model_to_dict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVR

import api.helpers.data_frame_helper as _df_helper
from api.helpers import to_utc_datetime
from api.models import CrowdForecast

from .data_source_data import DataSourceDataService as _DataSourceDataService

# from .user import UserService as _UserService

# _user_service = _UserService
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
    data_frame['day_of_week'] = data_frame['created_date'].dt.day_name()
    data_frame['date_hour'] = data_frame['created_date'].dt.hour
    data_frame['no_of_clients'].round(2)
    data_frame['is_weekend'] = data_frame['day_of_week'].apply(
        lambda x: _df_helper.item_in_list(x, ['Saturday', 'Sunday'])
    )
    del data_frame['id']
    del data_frame['data_source']
    for item in ['day_of_week', 'is_weekend']:
        data_frame[item] = _label_encoder.fit_transform(data_frame[item])
    return data_frame


def _create_next_week_dataframe():
    next_week_dataframe = DataFrame(
        {'created_date': _df_helper.get_future_timestamps()})
    next_week_dataframe['created_date'] = to_datetime(
        next_week_dataframe['created_date'], unit='s')
    next_week_dataframe['day_of_week'] = next_week_dataframe[
        'created_date'].dt.day_name()
    next_week_dataframe['date_hour'] = next_week_dataframe[
        'created_date'].dt.hour
    next_week_dataframe['is_weekend'] = next_week_dataframe[
        'day_of_week'].apply(
        lambda x: _df_helper.item_in_list(x, ['Saturday', 'Sunday'])
    )

    for item in ['day_of_week', 'is_weekend']:
        next_week_dataframe[item] = _label_encoder.fit_transform(
            next_week_dataframe[item])
    return next_week_dataframe


class ForecastService():
    def create_next_week_prediction():
        # retrieve the last three weeks for prediction
        try:
            start, end = _df_helper.get_past_weeks()
            data = _DataSourceDataService.get_all_data_from_data_source(
                _DataSourceDataService,
                data_source_id=2,
                limit=10000,
                start_date=start,
                end_date=end
            )

            data_frame = _transform_data_to_dataframe(data)
            data_frame = _add_time_characteristics(data_frame)
            next_week_dataframe = _create_next_week_dataframe()

            train, test = train_test_split(
                data_frame, test_size=0.25, shuffle=False)
            print(train)
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
                prediction_for_date_range=f"{start}-{end}",
                prediction_data=next_week_dataframe.to_json()
            )
            return model_to_dict(result)
        except Exception as err:
            print(err)
            raise ValueError(HTTPStatus.INTERNAL_SERVER_ERROR,
                             "Unable to create prediction for the next week.")