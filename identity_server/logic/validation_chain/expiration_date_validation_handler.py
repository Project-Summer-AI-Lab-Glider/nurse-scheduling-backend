import time
from typing import Optional

from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.expiration_date_validation_error import ExpirationDateValidatorError

class ExpirationDateValidator(Handler):
    def __init__(self):
        super().__init__()
        self.exp_time = 0.0

    def handle(self, exp_time, **kwargs) -> bool:
        self.exp_time = exp_time
        if not self._check_expire():
            return super().handle(**kwargs)
        else:
            raise ExpirationDateValidatorError()

    def _check_expire(self) -> bool:
        return time.time() > self.exp_time
