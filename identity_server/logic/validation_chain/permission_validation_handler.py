from typing import Optional, List

from identity_server.logic.validation_chain.permissions import Permissions
from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.permission_validation_error import PermissionValidatorError

class PermissionValidator(Handler):
    def __init__(self):
        super().__init__()
        self.permissions = ''
        self.excepted_permissions = [Permissions]

    def handle(self, permissions: [str], excepted_permissions: List[Permissions], **kwargs) -> bool:
        self.permissions = permissions
        self.excepted_permissions = excepted_permissions
        if self._validate_permissions():
            return super().handle(**kwargs)
        else:
            raise PermissionValidatorError()

    def _validate_permissions(self):
        for p in self.excepted_permissions:
            if p.value not in self.permissions:
                return False
        return True
