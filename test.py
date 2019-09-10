import time
import redis
import peewee
import os

from flask import Flask
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask('test')
cache = redis.Redis(host='redis', port=6379)
appName = app.name

db = peewee.MySQLDatabase(os.getenv("MYSQL_DATABASE"),
                          host="0.0.0.0",
                          port=3306,
                          user=os.getenv("MYSQL_USER"),
                          passwd=os.getenv("MYSQL_PASSWORD"))


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/')
def index():
    return 'Hello World, from App name {test1} and default name is {test2}.'.format(
        test1=os.getenv("MYSQL_PASSWORD"), test2=os.getenv("MYSQL_USER"))


@app.route('/counter')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)


# # Use venv in combination with docker.
# # venv used for separation during local development
# # Docker is used to create an isolated environment
# # Able to set host using flag "ENV FLASK_RUN_HOST X.X.X.X"
if __name__ == '__main__':
    app.run()
