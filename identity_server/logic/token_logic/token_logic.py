from identity_server.logic.token_logic.token_encoder import TokenEncoder
from identity_server.logic.token_logic.token_builder import TokenBuilder


class TokenLogic:
    def __init__(self) -> None:
        self._token_encoder = TokenEncoder()
        self._token_builder = TokenBuilder()

    def create_token(self, code):
        user_id = "ADMIN"           # TODO DB request to DB, based on code
        permissions = ["777"]         # TODO DB srequest to DB
        self._token_builder.init(user_id, permissions)
        return self._token_builder.generate_token()

    def refresh_token(self):
        return self._token_builder.generate_token()

    def revoke_token(self):
        return True, ''
