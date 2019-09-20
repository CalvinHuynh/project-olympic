import os
from http import HTTPStatus
from pathlib import Path

from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


api_version = os.getenv("FLASK_API_VERSION").strip() if os.getenv("FLASK_API_VERSION").strip() else "1.0.0"

class ErrorObject:
    def create_response(self, error_code: HTTPStatus, error_message: str):
        return {
            "apiVersion": api_version,
            "error": {
                "code": error_code,
                "message": error_message
            }
        }


class SuccessObject:
    def create_response(self, status_code: HTTPStatus, data: object):
        return {"apiVersion": api_version, "data": data}
