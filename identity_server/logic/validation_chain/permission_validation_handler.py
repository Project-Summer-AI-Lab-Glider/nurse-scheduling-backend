from typing import Optional

from identity_server.logic.validation_chain.handler import Handler


class PermissionValidator(Handler):
    def __init__(self):
        super().__init__()
        self.permissions = ''
        self.excepted_permissions = ''

    def handle(self, permissions: [str], excepted_permissions: [str], **kwargs) -> Optional[str]:
        self.permissions = permissions
        self.excepted_permissions = excepted_permissions
        if self._validate_permissions():
            return super().handle(**kwargs)
        else:
            raise Exception("Invalid Permissions")

    def _validate_permissions(self):
        for p in self.excepted_permissions:
            if p not in self.permissions:
                return False
        return True
