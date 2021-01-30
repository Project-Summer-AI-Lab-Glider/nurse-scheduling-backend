from identity_server.logic.session.revoked_token_provider import RevokedTokenProvider
from identity_server.logic.validation_chain.exceptions.validator_exceptions import RevokedTokenException
from identity_server.logic.validation_chain.handler import Handler


class TokenStatusValidator(Handler):
    def __init__(self):
        super().__init__()
        self.legal_signature = b''
        self.signature = b''

    def handle(self, token, **kwargs) -> bool:
        if RevokedTokenProvider().is_token_revoked(token):
            raise RevokedTokenException(token)
        return super().handle(token=token, **kwargs)
