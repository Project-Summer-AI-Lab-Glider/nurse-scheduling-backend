from typing import Optional

from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.validator_exceptions import HeaderValidationException


class HeaderValidator(Handler):
    def __init__(self):
        super().__init__()
        self.header = ''

    def handle(self, header: bytes, **kwargs) -> bool:
        self.header = header
        if self._validate_header():
            return super().handle(**kwargs)
        else:
            raise HeaderValidationException()

    def _validate_header(self) -> bool:
        return self.header == b'{"typ": "JWT", "alg": "HS256"}'
