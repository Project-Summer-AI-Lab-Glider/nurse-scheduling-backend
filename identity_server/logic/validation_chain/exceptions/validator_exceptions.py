from django.http import HttpResponseForbidden
from django.http.response import HttpResponse


class ValidatorException(Exception):
    """
    Base class for all exceptions thrown by validators
    """

    def response(self) -> HttpResponse:
        return HttpResponse(status=418, content="Brew your coffee by yourself!")


class HTTPRequestValidatorException(ValidatorException):
    def __init__(self):
        self.message = "Invalid HTTP request"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class TokenValidatorException(ValidatorException):
    def __init__(self):
        self.message = "Invalid Token"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class SignatureValidationException(ValidatorException):
    def __init__(self):
        self.message = "Invalid Signature"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class PermissionValidatorException(ValidatorException):
    def __init__(self):
        self.message = "Invalid Permissions"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class HeaderValidationException(ValidatorException):
    def __init__(self):
        self.message = "Invalid Header"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class ExpirationDateValidatorException(ValidatorException):
    def __init__(self):
        self.message = "Token Expired"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')
