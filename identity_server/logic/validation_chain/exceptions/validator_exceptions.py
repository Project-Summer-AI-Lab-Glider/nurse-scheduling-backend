from django.http import HttpResponseForbidden


class HTTPRequestValidatorException(Exception):
    def __init__(self):
        self.message = "Invalid HTTP request"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class TokenValidatorException(Exception):
    def __init__(self):
        self.message = "Invalid Token"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class SignatureValidationException(Exception):
    def __init__(self):
        self.message = "Invalid Signature"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class PermissionValidatorException(Exception):
    def __init__(self):
        self.message = "Invalid Permissions"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class HeaderValidationException(Exception):
    def __init__(self):
        self.message = "Invalid Header"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')


class ExpirationDateValidatorException(Exception):
    def __init__(self):
        self.message = "Token Expired"
        super().__init__(self.message)

    def response(self):
        return HttpResponseForbidden(f'<h1>{self.message}</h1>')
