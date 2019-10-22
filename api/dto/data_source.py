from .user import UserDto


class CreateDataSourceDto:

    source: str
    description: str
    user: UserDto

    def __init__(self, source, description, user: UserDto):
        self.source = source
        self.description = description
        self.user = user


class CreateDataSourceDataDto:
    no_of_clients: int

    def __init__(self, no_of_clients):
        self.no_of_clients = no_of_clients
