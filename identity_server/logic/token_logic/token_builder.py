import base64
from enum import Enum
import hmac
from identity_server.logic.validation_chain.endpoint_decorator import Permissions
import json
import time
from typing import List, Tuple
from nurse_scheduling_backend.settings import SECRET_KEY


class TokenType(Enum):
    Bearer = "bearer"


class TokenBuilder:

    def __init__(self, user_id: int, token_type: TokenType = TokenType.Bearer) -> None:
        self.permissions = []
        self.token_type = token_type
        self.user_id = user_id
        self.header = self._create_header()
        self.payload = ''.encode('utf-8')
        self._seconds_to_expire = None

    def add_permissions(self, permissions: List[Permissions]) -> 'TokenBuilder':
        self.permissions.extend(permissions)
        return self

    def set_expiration_time(self, expire_time: int) -> 'TokenBuilder':
        self._seconds_to_expire = expire_time
        return self

    def generate(self) -> str:
        token_data = self._generate_token()
        self._clear()
        return token_data

    @staticmethod
    def _base64_encode(statement: bytes) -> str:
        return base64.urlsafe_b64encode(statement).decode().strip('=')

    def _clear(self):
        self.expiration_time = 0
        self.permissions.clear()

    def _create_header(self):
        return json.dumps(
            {'typ': 'JWT', 'alg': 'HS256'}).encode('utf-8')

    def _generate_payload(self) -> None:
        self.payload = json.dumps({
            "userId": self.user_id,
            "permissions": self.permissions,
            "exp": time.time() + self._seconds_to_expire
        }).encode('utf-8')

    def _create_signature(self, unsigned_token: str) -> bytes:
        return hmac.new(bytes(SECRET_KEY, 'latin-1'), unsigned_token.encode('utf-8'), 'sha256').digest()

    def _generate_token(self) -> Tuple[str, TokenType, int]:
        if not self._seconds_to_expire:
            raise Exception("Expiration time is missing")

        header_enc = TokenBuilder._base64_encode(self.header)
        payload_enc = TokenBuilder._base64_encode(self.payload)
        unsigned_token = header_enc + '.' + payload_enc
        signature = self._create_signature(unsigned_token)
        signature_enc = TokenBuilder._base64_encode(signature)
        token = unsigned_token + '.' + signature_enc
        self.token = token
        return self.token, self.token_type, self._seconds_to_expire

    def __str__(self) -> str:
        return self.token
