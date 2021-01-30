from identity_server.logic.validation_chain.token_status_validator import TokenStatusValidator
from identity_server.logic.validation_chain.token_validator_handler import TokenValidator
from identity_server.logic.validation_chain.signature_validation_handler import SignatureValidator
from identity_server.logic.validation_chain.permissions import Permissions
from identity_server.logic.validation_chain.permission_validation_handler import PermissionValidator
from identity_server.logic.validation_chain.header_validation_handler import HeaderValidator
from identity_server.logic.validation_chain.expiration_date_validation_handler import ExpirationDateValidator
from identity_server.logic.validation_chain.http_request_validator_handler import HttpRequestValidator


from .exceptions.validator_exceptions import *

from enum import Enum
from typing import Callable, Dict, List
import functools
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotFound


class HttpMethod(Enum):
    """
    Methods allowed on Identity Service
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'
    PUT = 'PUT'


class Validator:
    def __init__(self):
        self.validation_chain = [HttpRequestValidator(), TokenStatusValidator(), TokenValidator(), SignatureValidator(), HeaderValidator(),
                                 PermissionValidator(), ExpirationDateValidator()]
        for i in range(len(self.validation_chain) - 1):
            self.validation_chain[i].set_next(self.validation_chain[i + 1])

    def validate(self, request, permissions):
        return self.validation_chain[0].handle(request, permissions)


def endpoint(*allowed_methods: HttpMethod, permissions: List[Permissions] = None):
    def endpoint_wrapper(func: Callable[[HttpRequest, Dict[str, any]], HttpResponse]):
        @functools.wraps(func)
        def handler(request: HttpRequest, **kwargs):
            if request.method not in [item.value for item in allowed_methods]:
                return HttpResponseNotFound(f"<h1>Method {request.method} {request.path} does not exists</h1>")
            if permissions is not None:
                try:
                    Validator().validate(request, permissions)
                except ValidatorException as e:
                    return e.response()
            splited_meta = request.META.setdefault(
                'HTTP_AUTHORIZATION', " ").split(' ')
            if len(splited_meta) > 1:
                token = splited_meta[1]
            else:
                token = ''

            return func(request, token=token, **kwargs)

        return handler
    return endpoint_wrapper
