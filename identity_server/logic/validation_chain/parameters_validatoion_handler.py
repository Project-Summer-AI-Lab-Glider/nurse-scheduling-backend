from django.http.request import HttpRequest
from typing import Optional, List

from identity_server.logic.validation_chain.permissions import Permissions
from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.validator_exceptions import ParameterValidationException


class ParametersValidator(Handler):
    def __init__(self):
        super().__init__()
        self.metadata = {}
        self.authorization_key = 'HTTP_AUTHORIZATION'

    def handle(self, request_meta, permissions: List[Permissions], **kwargs) -> bool:
        try:
            method, token = request_meta['HTTP_AUTHORIZATION'].split(' ')
        except Exception:
            if self.authorization_key in request_meta:
                method = request_meta['HTTP_AUTHORIZATION']
            token = ''

        self.metadata.update({'method': method, 'token': token, 'excepted_permissions': permissions})
        try:
            return super().handle(**kwargs)
        except Exception:
            raise ParameterValidationException()