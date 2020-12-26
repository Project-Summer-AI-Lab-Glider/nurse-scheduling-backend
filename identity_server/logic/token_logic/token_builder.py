import base64
import hmac
import json


class TokenBuilder:
    def __init__(self) -> None:
        self.SECRET_KEY = 'DOROGOJTYTOCHNOPOZABOTILSYAOZASHCHITE?'  # TODO REMOVE THIS
        self.permissions = []
        self.user_id = ''
        self.header = json.dumps(
            {'typ': 'JWT', 'alg': 'HS256'}).encode('utf-8')
        self.payload = ''.encode('utf-8')
        self.token = ''
        self.initialized = False

    def init(self, permissions: str, user_id: str) -> None:
        self._add_permissions(permissions)
        self._add_user_id(user_id)
        self._generate_payload()
        self.initialized = True

    @staticmethod
    def _base64_encode(statement: bytes) -> str:
        return base64.urlsafe_b64encode(statement).decode().strip('=')

    def _add_permissions(self, permissions: str) -> None:
        self.permissions.extend(permissions)

    def _add_user_id(self, user_id: str) -> None:
        self.user_id = user_id

    def _generate_payload(self) -> None:
        self.payload = json.dumps(
            {"userId": self.user_id, "permissions": self.permissions}).encode('utf-8')

    def _create_signature(self, unsigned_token: str) -> bytes:
        return hmac.new(bytes(self.SECRET_KEY, 'latin-1'), unsigned_token.encode('utf-8'), 'sha256').digest()

    def generate_token(self) -> str:
        if not self.initialized:
            raise Exception("PLEASE INITIALIZE THE BUILDER FIRST")
        header_enc = TokenBuilder._base64_encode(self.header)
        payload_enc = TokenBuilder._base64_encode(self.payload)

        unsigned_token = header_enc + '.' + payload_enc
        signature = self._create_signature(unsigned_token)
        signature_enc = TokenBuilder._base64_encode(signature)

        token = unsigned_token + '.' + signature_enc
        self.token = token
        return self.token

    def __str__(self) -> str:
        return self.token
