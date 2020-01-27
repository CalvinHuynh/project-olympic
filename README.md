# Project Olympic
This is an API that periodically looks up the number of clients that are currently connected to the network. It also retrieves the current weather and the weather forecast from [OpenWeatherMap](https://openweathermap.org/). 

## Technologies
Exploratory project to experiment with unfamiliar technologies such as:
* Docker: Used to create a portable application that can run in any environment.
* Docker-compose: Used for running multiple docker containers. This project's compose file will create two Docker containers, one docker container running the application inside a Fedora environment and one MySQL container.
* Python: The python language is chosen due to the numerous mathematical and scientific packages. Python is also chosen due to my wish to learn a new programming language.
* Google Cloud (Cloud SQL and Compute Engine): Google's solutions are used as Incentro is a Google Partner.

## Python packages
* Flask web framework (and other extensions extending Flask):
* Peewee ORM
* Scikit-learn 
* Pandas
* Dash

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



## Formatting and Linting
In this project [yapf](https://github.com/google/yapf) is used to format the code.  
For linting [flake8](https://gitlab.com/pycqa/flake8) is used. Before committing, please ensure that the codebase contains no linting errors. To do so, run the following command `$ flake8` at the root of the project.
