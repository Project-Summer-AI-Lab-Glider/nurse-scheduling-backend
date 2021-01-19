import base64
import hmac
import json
from typing import Tuple
from nurse_scheduling_backend.settings import SECRET_KEY

from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.token_validator_error import TokenValidatorError


class TokenValidator(Handler):

    def __init__(self, next_item=None) -> None:
        super().__init__(next_item)
        self.permissions = []
        self.user_id = ''
        self.header = ''
        self.payload = {}
        self.token = ''
        self.exp_time = 0.0
        self.legal_signature = ''
        self.signature = ''
        self.initialized = False

    def handle(self, token, **kwargs):
        self.init(token)
        if self._validate_token():
            return super().handle(**{**kwargs,
                                     'permissions': self.permissions,
                                     'header': self.header,
                                     'exp_time': self.exp_time,
                                     'signature': self.signature,
                                     'legal_signature': self.legal_signature,
                                     })
        else:
            raise TokenValidatorError()

    def init(self, token) -> None:
        self.token = token
        self.initialized = True

    @staticmethod
    def _base64_decode(statement: str) -> bytes:
        statement += '=' * (-len(statement) % 4)
        return base64.urlsafe_b64decode(statement)

    def _read_payload(self, payload) -> None:
        self.payload = json.loads(payload.decode("utf-8"))

    def _create_signature(self, unsigned_token: str) -> bytes:
        return hmac.new(bytes(SECRET_KEY, 'latin-1'), unsigned_token.encode('utf-8'), 'sha256').digest()

    def _extract_payloads(self) -> Tuple[str, str, str]:
        self.user_id = self.payload['userId']
        self.permissions = self.payload['permissions']
        self.exp_time = self.payload['exp']
        return self.user_id, self.permissions, self.exp_time

    def _validate_token(self):
        try:
            if not self.initialized:
                raise Exception("PLEASE INITIALIZE THE VALIDATOR FIRST")

            header_enc, payload_enc, signature_enc = self.token.split('.')
            payload = self._base64_decode(payload_enc)
            self._read_payload(payload)
            self.header = self._base64_decode(header_enc)
            self.signature = self._base64_decode(signature_enc)
            self.legal_signature = self._create_signature(
                header_enc + '.' + payload_enc)
            self._extract_payloads()
            return True
        except Exception as e:
            print(e)
            return False

    def __str__(self) -> str:
        return self.token
