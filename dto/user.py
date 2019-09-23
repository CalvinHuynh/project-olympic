class UserDto:
    id: int
    username: str

    # email: str

    def __init__(
            self,
            id,
            username,
            # email
    ):
        self.id = id
        self.username = username
        # self.email = email
