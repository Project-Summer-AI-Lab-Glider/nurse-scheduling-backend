from identity_server.logic.validation_chain.permissions import Permissions
from .exceptions.validator_exceptions import *
from enum import Enum
from typing import Callable, Dict, List
import functools
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotFound
from .validator import Validator


class HttpMethod(Enum):
    """
    Methods allowed on Identity Service
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'
    PUT = 'PUT'


def endpoint(*allowed_methods: HttpMethod, permissions: List[Permissions] = None):
    def endpoint_wrapper(func: Callable[[HttpRequest, str, Dict[str, any]], HttpResponse]):
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

            return func(request, **{'token': token, **kwargs})

        return handler

    return endpoint_wrapper
