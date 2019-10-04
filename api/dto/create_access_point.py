from .user import UserDto


class CreateAccessPointDto:

    ip_addr: str
    description: str
    user: UserDto

    def __init__(self, ip_addr, description, user: UserDto):
        self.ip_addr = ip_addr
        self.description = description
        self.user = user
