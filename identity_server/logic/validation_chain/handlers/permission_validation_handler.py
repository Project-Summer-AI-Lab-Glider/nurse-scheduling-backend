from typing import List
from identity_server.logic.validation_chain.permissions import Permissions
from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.validator_exceptions import PermissionValidatorException


class PermissionValidator(Handler):
    def __init__(self):
        super().__init__()

    def handle(self, permissions: List[str], excepted_permissions: List[Permissions], **kwargs) -> bool:
        if self._validate_permissions(permissions, excepted_permissions):
            return super().handle(**kwargs)
        else:
            raise PermissionValidatorException()

    @staticmethod
    def _validate_permissions(permissions, excepted_permissions):
        for p in excepted_permissions:
            if p.value not in permissions:
                return False
        return True
