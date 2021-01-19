from identity_server.logic.validation_chain.token_validator_handler import TokenValidator
from identity_server.logic.validation_chain.signature_validation_handler import SignatureValidator
from identity_server.logic.validation_chain.permissions import Permissions
from identity_server.logic.validation_chain.permission_validation_handler import PermissionValidator
from identity_server.logic.validation_chain.header_validation_handler import HeaderValidator
from identity_server.logic.validation_chain.expiration_date_validation_handler import ExpirationDateValidator
from identity_server.logic.validation_chain.http_validator_handler import HttpValidator
from enum import Enum
from typing import Callable, List, Dict
from typing import Callable, Dict, List
import functools
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseNotFound


class HttpMethod(Enum):
    """
    Methods allowed on Identity Service
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'


class Validator:
    def __init__(self):
        self.request = {}
        self.validation_chain = [HttpValidator(), TokenValidator(), SignatureValidator(), HeaderValidator(),
                                 PermissionValidator(), ExpirationDateValidator()]
        for i in range(len(self.validation_chain) - 1):
            self.validation_chain[i].set_next(self.validation_chain[i + 1])

    def validate(self, request, permissions):
        self.request, next_validator = self.validation_chain[0].handle(request, permissions)
        return next_validator


def endpoint(*allowed_methods: HttpMethod, permissions: List[Permissions] = None):
    def endpoint_wrapper(func: Callable[[HttpRequest, Dict[str, any]], HttpResponse]):
        @functools.wraps(func)
        def handler(request: HttpRequest, **kwargs):
            if request.method not in [item.value for item in allowed_methods]:
                return HttpResponseNotFound(f"<h1>Method {request.method} {request.path} does not exists</h1>")
            if permissions is not None:
                try:
                    Validator().validate(request, permissions)
                except Exception:
                    return HttpResponseForbidden(f"Not authorized")
            return func(request, **kwargs)
        return handler

    return endpoint_wrapper
