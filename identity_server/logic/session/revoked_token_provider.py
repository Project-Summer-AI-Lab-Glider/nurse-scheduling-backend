
from identity_server.logic.session.singleton import Singleton


class RevokedTokenProvider(metaclass=Singleton):
    _revoked_access_tokens = []

    def add_revoked_token(self, token):
        self._revoked_access_tokens.append(token)

    def is_token_revoked(self, token):
        return token in self._revoked_access_tokens
