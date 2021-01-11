class ParameterValidationError(Exception):
    def __init__(self):
        super().__init__("Parameter validation error")
