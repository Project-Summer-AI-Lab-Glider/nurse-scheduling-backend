class TokenLogicException(Exception):
    """
    Base class for exceptions that could be thrown by token logic
    """


class RefreshTokenNotBelongsToAnyUser(TokenLogicException):
    """
    Exception thrown when received refresh token does not belongs 
    to any user in the application
    """
