import base64
import hmac
import json
import time
from typing import Any

from identity_server.logic.validation_chain.handler import Handler


class TokenValidator(Handler):

    def __init__(self, next_item=None) -> None:
        super().__init__(next_item)
        self.SECRET_KEY = 'DOROGOJTYTOCHNOPOZABOTILSYAOZASHCHITE?'  # TODO REMOVE THIS
        self.permissions = []
        self.user_id = ''
        self.header = ''
        self.payload = {}
        self.token = ''
        self.exp_time = 0.0
        self.initialized = False

    def handle(self, request: Any):
        self.init(request)
        if self._validate_token():
            return super().handle(self.permissions)
        else:
            return False

    def init(self, token) -> None:
        self.token = token
        self.initialized = True

    @staticmethod
    def _base64_decode(statement: str) -> bytes:
        statement += '=' * (-len(statement) % 4)
        return base64.urlsafe_b64decode(statement)

    @staticmethod
    def _compare_signatures(sign1: bytes, sign2: bytes) -> bool:
        return hmac.compare_digest(sign1, sign2)

    def _read_payload(self, payload) -> None:
        self.payload = json.loads(payload.decode("utf-8"))

    def _create_signature(self, unsigned_token: str) -> bytes:
        return hmac.new(bytes(self.SECRET_KEY, 'latin-1'), unsigned_token.encode('utf-8'), 'sha256').digest()

    def _extract_payloads(self) -> None:
        self.user_id = self.payload['userId']
        self.permissions = self.payload['permissions']
        self.exp_time = self.payload['exp']

    def _check_expire(self) -> bool:
        return time.time() > self.exp_time

    def _validate_header(self) -> bool:
        return self.header == b'{"typ": "JWT", "alg": "HS256"}'

    def _validate_token(self):
        try:
            if not self.initialized:
                raise Exception("PLEASE INITIALIZE THE VALIDATOR FIRST")
            header_enc, payload_enc, signature_enc = self.token.split('.')
            payload = self._base64_decode(payload_enc)
            self._read_payload(payload)
            self.header = self._base64_decode(header_enc)
            signature = self._base64_decode(signature_enc)
            legal_signature = self._create_signature(header_enc + '.' + payload_enc)
            if not self._compare_signatures(legal_signature, signature):
                raise Exception("Invalid Signature")
            if not self._validate_header():
                raise Exception("Invalid Header")
            self._extract_payloads()
            if self._check_expire():
                raise Exception("Token expired")
            return True
        except Exception as e:
            print(e)
            return False

    def __str__(self) -> str:
        return self.token

