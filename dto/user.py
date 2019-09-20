class UserDto:
    identifier: int
    username: str

    # email: str

    def __init__(
            self,
            identifier,
            username,
            # email
    ):
        UserDto.identifier = identifier
        UserDto.username = username
        # UserDto.email = email
