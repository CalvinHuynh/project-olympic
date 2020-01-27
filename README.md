# Project Olympic
The goal of this project is to create an API that offers endpoints for data acquisition and predictions.  
The `api/jobs.py` file contains three cronjobs that periodically do the following:
1. Retrieve the current weather every 10th minute
2. Retrieve the 5-day weather forecast every day at 20:00
3. Retrieve the number of clients from the web portal every 10th minute
The current weather and the weather forecast are retrieved from [OpenWeatherMap](https://openweathermap.org/). 

## Technologies
Exploratory project to experiment with unfamiliar technologies such as:
* Docker: Used to create a portable application that can run in any environment.
* Docker-compose: Used for running multiple docker containers. This project's compose file will create two Docker containers, one docker container running the application inside a Fedora environment and one MySQL container.
* Python: The python language is chosen due to the numerous mathematical and scientific packages. Python is also chosen due to my wish to learn a new programming language.
* Google Cloud (Cloud SQL and Compute Engine): Google's solutions are used as Incentro is a Google Partner.

## Python packages used
* Flask web framework (and other extensions extending Flask): Flask is chosen due to the freedom that the framework offers. The project is actively being developed on Git and it has a large community.
* Peewee ORM: Peewee is chosen over other ORM's (SQLAlchemy, Django) as Peewee has a smaller footprint and has a low learning curve for someone new to Python.
* Scikit-learn: This library offers several regression methods for this project to use. This library is chosen due to the ease to use, a low learning curve and a handy graph to help the user chose the correct algorithm.
* Pandas: Library used for creating data frames. It is used to analyze patterns & trends and to prepare the data for machine learning.
* Dash: Package written on top of Flask, Plotly.js and React.js. Used for building data visualisation apps.

## Requirement
* Python 3.3 or higher
* Docker-compose *version TBA*
* Docker *version TBA*

## Quick start
* CD into the project
* Create a copy of the `.env.template` file by running the following command `$ mv .env.template .env`
* Fill in the fields of the `.env` file
  * Optionally change the ports in the `docker-compose.yml` file.
* Start the docker containers by running the following command `$ docker-compose up`
* Go to `localhost:${PORT_NUMBER}` to access the API.

## Development setup
To get the required packages to start developing locally, run the following command:  
```bash
python3 -m venv /path/to/virtual/env # creates a virtual environment using python3
source /path/to/virtual/env/bin/activate # activates the virtual environment
pip3 install -r requirements.txt # installs the packages recursively to the virtual environment
```
After installing the packages, run the following command in the terminal to start the server:
```bash
cd /path/to/root/of/project
export FLASK_APP="./api/app.py" # sets the entry point for Flask in the environment
python -m flask run # starts the flask server
```
Access the server at the URL shown in the output of the terminal.


## Formatting and Linting
In this project [yapf](https://github.com/google/yapf) is used to format the code.  
For linting [flake8](https://gitlab.com/pycqa/flake8) is used. Before committing, please ensure that the codebase contains no linting errors. To do so, run the following command `$ flake8` at the root of the project.
