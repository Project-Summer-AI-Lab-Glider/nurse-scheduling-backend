import json
from django.http import HttpResponse
from identity_server.logic.validation_chain.endpoint_decorator import (
    HttpMethod, endpoint)


@endpoint(HttpMethod.GET)
def is_active(self, **kwargs):
    return HttpResponse(json.dumps({'is_active': True}))
