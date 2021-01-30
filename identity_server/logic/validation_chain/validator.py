from identity_server.logic.validation_chain.handlers.token_status_validator import TokenStatusValidator
from identity_server.logic.validation_chain.handlers.token_validator_handler import TokenValidator
from identity_server.logic.validation_chain.handlers.signature_validation_handler import SignatureValidator
from identity_server.logic.validation_chain.handlers.permission_validation_handler import PermissionValidator
from identity_server.logic.validation_chain.handlers.header_validation_handler import HeaderValidator
from identity_server.logic.validation_chain.handlers.expiration_date_validation_handler import ExpirationDateValidator
from identity_server.logic.validation_chain.handlers.http_request_validator_handler import HttpRequestValidator


class Validator:
    def __init__(self):
        self.validation_chain = [HttpRequestValidator(), TokenStatusValidator(), TokenValidator(), SignatureValidator(),
                                 HeaderValidator(), PermissionValidator(), ExpirationDateValidator()]
        for i in range(len(self.validation_chain) - 1):
            self.validation_chain[i].set_next(self.validation_chain[i + 1])

    def validate(self, request, permissions):
        return self.validation_chain[0].handle(request, permissions)