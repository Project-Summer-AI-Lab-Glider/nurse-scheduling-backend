import functools
from django.http import request
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotFound
from typing import Callable, List
from enum import Enum
import json


def validate(func):
    def wrapper():
        func()


    return wrapper
