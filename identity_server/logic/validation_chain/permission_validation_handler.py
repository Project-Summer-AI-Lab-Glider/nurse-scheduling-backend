from typing import Any, Optional
from identity_server.logic.validation_chain.handler import Handler


class PermissionValidator(Handler):
    def __init__(self):
        super().__init__()
        self.permissions = ''

    def handle(self, request: Any) -> Optional[str]:
        self.permissions = request
        return True
