from apscheduler.schedulers.background import BackgroundScheduler

from api.services import DataSourceDataService as _DataSourceDataService
from api.services import WeatherService as _WeatherService
# from api.wrapper.browser.web import AutomatedWebDriver, WebDriverType

from .settings import NUMBER_OF_BACKGROUND_WORKERS

_weather_service = _WeatherService
_data_source_data_service = _DataSourceDataService

executors = {
    'default': {
        'type': 'threadpool',
        'max_workers': NUMBER_OF_BACKGROUND_WORKERS
    },
}

bg_scheduler = BackgroundScheduler(executors=executors)


@bg_scheduler.scheduled_job('cron', minute='*/10')
def get_weather():
    _weather_service.get_current_weather(_weather_service)


@bg_scheduler.scheduled_job('cron', minute='0', hour='20')
def get_weather_forecast():
    _weather_service.get_weather_forecast_5d_3h(_weather_service)


# @bg_scheduler.scheduled_job('cron', minute='*/10')
# def get_clients():
#     from api.dto import CreateDataSourceDataDto
#     web_driver = AutomatedWebDriver(UNIFI_ADDRESS, WebDriverType.FIREFOX)
#     dto = CreateDataSourceDataDto(web_driver.get_clients())
#     _data_source_data_service.post_data(_data_source_data_service, 1, dto)
