from identity_server.logic.token_logic.token_encoder import TokenEncoder
from identity_server.logic.token_logic.token_builder import TokenBuilder


class TokenLogic:
    def __init__(self) -> None:
        self._token_encoder = TokenEncoder()
        self._token_builder = TokenBuilder()

    def create_token(self, code):
        # Placeholder
        token = {}
        return self._token_encoder.encode(token)

    def refresh_token(self):
        return ''

    def revoke_token(self):
        return True, ''
