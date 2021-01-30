class UserLogicException(Exception):
    """
    Base class to represent errors thrown by user logic
    """

    def __init__(self, user, *args: object) -> None:
        super().__init__(*args)
        self.user = user


class UserAlreadyExists(UserLogicException):
    def __str__(self) -> str:
        return f"User already exists {self.user}"


class UserNotExists(UserLogicException):
    def __str__(self) -> str:
        return f"User not exists {self.user}"
