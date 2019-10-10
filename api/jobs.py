from datetime import datetime

from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from api.services.scheduler import test_scheduler
from api.services import WeatherService as _WeatherService
from .settings import NO_OF_BACKGROUND_WORKERS

_weather_service = _WeatherService

executors = {
    'default': {'type': 'threadpool', 'max_workers': NO_OF_BACKGROUND_WORKERS},
}

bg_scheduler = BackgroundScheduler(executors=executors)

@bg_scheduler.scheduled_job('interval', seconds=10)
def do_test_function():
    test_scheduler(test_scheduler)

@bg_scheduler.scheduled_job('cron' , minute='10')
def do_second_function():
    _weather_service.get_current_weather(_weather_service)
