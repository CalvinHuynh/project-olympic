# Project project
Exploratory project to experiment with unfamiliar technologies such as:
* Docker (and Docker-compose)
* Python
* Flask web framework (and other extensions extending Flask)
* Peewee ORM.* Redis


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