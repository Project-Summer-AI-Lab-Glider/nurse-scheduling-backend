import functools
from django.http import request
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotFound
from typing import Callable, List
from enum import Enum
import json


class HttpMethod(Enum):
    """
    Methods allowed on Identity Service
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'


def endpoint(*allowed_methods: List[HttpMethod]):
    def endpoint_wrapper(func: Callable[[HttpRequest], HttpResponse]):
        @functools.wraps(func)
        def handler(request: HttpRequest):
            if request.method not in [item.value for item in allowed_methods]:
                return HttpResponseNotFound(f"<h1>Method {request.method} {request.path} does not exists</h1>")
            return func(request)
        return handler
    return endpoint_wrapper
