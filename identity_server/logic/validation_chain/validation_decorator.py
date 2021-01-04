from enum import Enum

from identity_server.logic.validation_chain.permission_validation_handler import PermissionValidator
from identity_server.logic.validation_chain.token_validator_handler import TokenValidator


class HttpMethod(Enum):
    """
    Methods allowed on Identity Service
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'


class Validator:
    def __init__(self, request: str):
        self.validation_chain = [TokenValidator(), PermissionValidator()]
        self.request = request
        for i in range(len(self.validation_chain) - 1):
            self.validation_chain[i].set_next(self.validation_chain[i + 1])

    def validate(self):
        return self.validation_chain[0].handle(self.request)


v = Validator(
    'eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJIUzI1NiJ9.eyJ1c2VySWQiOiAidXNlciIsICJwZXJtaXNzaW9ucyI6IFsiUiIsICJXIl0sICJleHAiOiAxNjA5Nzc1NTc2LjAxNjg3OTN9.XMoe5TPjnXZPo4WL8q_FjnwLCMOBDRzR0eCWYBjAhxg')
print(v.validate())
