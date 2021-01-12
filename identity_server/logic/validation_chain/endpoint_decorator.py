from identity_server.logic.validation_chain.token_validator_handler import TokenValidator
from identity_server.logic.validation_chain.signature_validation_handler import SignatureValidator
from identity_server.logic.validation_chain.permissions import Permissions
from identity_server.logic.validation_chain.permission_validation_handler import PermissionValidator
from identity_server.logic.validation_chain.header_validation_handler import HeaderValidator
from identity_server.logic.validation_chain.expiration_date_validation_handler import ExpirationDateValidator
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
    def __init__(self, metadata: Dict[str, str]):
        self.validation_chain = [TokenValidator(), SignatureValidator(), HeaderValidator(), PermissionValidator(),
                                 ExpirationDateValidator()]
        self.request = metadata
        for i in range(len(self.validation_chain) - 1):
            self.validation_chain[i].set_next(self.validation_chain[i + 1])

    def validate(self):
        return self.validation_chain[0].handle(**self.request)


def endpoint(*allowed_methods: HttpMethod, permissions: List[Permissions] = None):
    def endpoint_wrapper(func: Callable[[HttpRequest, Dict[str, any]], HttpResponse]):
        @functools.wraps(func)
        def handler(request: HttpRequest, **kwargs):
            if request.method not in [item.value for item in allowed_methods]:
                return HttpResponseNotFound(f"<h1>Method {request.method} {request.path} does not exists</h1>")
            if permissions is not None:
                token_parts = request.META.setdefault(
                    'HTTP_AUTHORIZATION', '').split(' ')
                if len(token_parts) == 2:
                    method, token = token_parts
                else:
                    method, token = token_parts[0], ''
                metadata = {'method': method, 'token': token,
                            'excepted_permissions': permissions}
                try:
                    Validator(metadata).validate()
                except Exception as e:
                    print(e)
                    return HttpResponseForbidden(f"Not authorized")
            return func(request, **kwargs)
        return handler

    return endpoint_wrapper
