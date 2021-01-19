class ExpirationDateValidatorError(Exception):
    def __init__(self):
        super().__init__("Token Expired")
