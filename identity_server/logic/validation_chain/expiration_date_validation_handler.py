import time
from typing import Optional

from identity_server.logic.validation_chain.handler import Handler


class PermissionValidator(Handler):
    def __init__(self):
        super().__init__()
        self.exp_time = 0.0

    def handle(self, exp_time, **kwargs) -> Optional[str]:
        self.exp_time = exp_time
        if self._check_expire():
            return super().handle(**kwargs)
        else:
            raise Exception("Token Expired")

    def _check_expire(self) -> bool:
        return time.time() > self.exp_time
