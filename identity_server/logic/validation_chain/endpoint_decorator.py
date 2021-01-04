import functools
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotFound
from typing import Callable, List
from enum import Enum

from identity_server.logic.validation_chain.permission_validation_handler import PermissionValidator
from identity_server.logic.validation_chain.token_validator_handler import TokenValidator


class Permissions(Enum):
    CONTACTS_READ = "CONTACTS_READ",
    CONTACTS_WRITE = "CONTACTS_WRITE",
    USER_READ = "USER_READ",
    USER_ADD = "USER_ADD"


class HttpMethod(Enum):
    """
    Methods allowed on Identity Service
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'


class Validator:
    def __init__(self, request: {}):
        self.validation_chain = [TokenValidator(), PermissionValidator()]
        self.request = request
        for i in range(len(self.validation_chain) - 1):
            self.validation_chain[i].set_next(self.validation_chain[i + 1])

    def validate(self):
        return self.validation_chain[0].handle(**self.request)


def endpoint(*allowed_methods: HttpMethod, permissions: List[Permissions] = None):
    def endpoint_wrapper(func: Callable[[HttpRequest], HttpResponse]):
        @functools.wraps(func)
        def handler(request: HttpRequest):
            if request.method not in [item.value for item in allowed_methods]:
                return HttpResponseNotFound(f"<h1>Method {request.method} {request.path} does not exists</h1>")
            if permissions is not None:
                metadata = {}
                method, token = request.META['Authorization'].split(' ')
                metadata.update({'method': method, 'token': token, 'excepted_permissions': permissions})
                try:
                    Validator(metadata).validate()
                    return func(request)
                except Exception as e:
                    print(e)
                    print("NOT VALIDATED")

        return handler

    return endpoint_wrapper
