# Project Olympic
This is an API that periodically looks up the number of clients that are currently connected to the network. It also retrieves the current weather and the weather forecast from [OpenWeatherMap](https://openweathermap.org/).

## Technologies
Exploratory project to experiment with unfamiliar technologies such as:
* Docker (and Docker-compose)
* Python
* Flask web framework (and other extensions extending Flask)
* Peewee ORM
* Google Cloud (Cloud SQL and Compute Engine)

## Requirement
* Python 3.3 or higher
* Docker-compose *version TBA*
* Docker *version TBA*

## Setup
* CD into the project
* Create a copy of the `.env.template` file by running the following command `$ mv .env.template .env`
* Fill in the fields of the `.env` file
  * Optionally change the ports in the `docker-compose.yml` file.
* Start the docker containers by running the following command `$ docker-compose up`
* Go to `localhost:${PORT_NUMBER}` to access the API.

## Formatting and Linting
In this project [yapf](https://github.com/google/yapf) is used to format the code.  
For linting [flake8](https://gitlab.com/pycqa/flake8) is used. Before commiting, please ensure that the code base contains no linting errors. To do so, run the following command `$ flake8` at the root of the project.
