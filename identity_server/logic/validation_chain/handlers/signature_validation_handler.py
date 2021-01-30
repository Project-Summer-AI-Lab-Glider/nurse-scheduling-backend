import hmac
from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.validator_exceptions import SignatureValidationException


class SignatureValidator(Handler):
    def __init__(self):
        super().__init__()
        self.legal_signature = b''
        self.signature = b''

    @staticmethod
    def _compare_signatures(sign1: bytes, sign2: bytes) -> bool:
        return hmac.compare_digest(sign1, sign2)

    def handle(self, legal_signature: bytes,
               signature: bytes, **kwargs) -> bool:
        self.legal_signature = legal_signature
        self.signature = signature
        if self._compare_signatures(self.legal_signature, self.signature):
            return super().handle(**kwargs)
        else:
            raise SignatureValidationException()
