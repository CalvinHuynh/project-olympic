from .user import UserDto

class CreateAccessPointDto:
    description: str
    user: UserDto

    def __init__(self, description, user: UserDto):
        CreateAccessPointDto.description = description
        CreateAccessPointDto.user = user
