from models import User

class CreateAccessPointDto:
    def __init__(self, description, user: User):
        self.description = description
        self.user = user
