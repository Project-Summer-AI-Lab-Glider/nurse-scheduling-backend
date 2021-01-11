from typing import List, Tuple
from identity_server.logic.validation_chain.endpoint_decorator import Permissions
from identity_server.logic.token_logic.token_encoder import TokenEncoder
from identity_server.logic.token_logic.token_builder import TokenBuilder, TokenType


class TokenLogic:
    def __init__(self) -> None:
        self._token_encoder = TokenEncoder()

    def create_tokens(self, refresh_token) -> Tuple[str, TokenType, int, str]:
        """
        Creates new pair of tokens based on refresh token
        """
        user_id, permissions, client_id = self._get_associated_user(
            refresh_token)
        builder = TokenBuilder(user_id, TokenType.Bearer)
        rotated_refresh_token = self._create_refresh_token(
            builder, client_id, user_id)
        access_token, token_type, seconds_to_expire = self._create_access_token(
            builder, permissions)
        return access_token, token_type, seconds_to_expire, rotated_refresh_token

    def create_refresh_token(self, user_id, client_id) -> str:
        """
        Creates new refresh token for user with given id and refresh token
        """
        builder = TokenBuilder(user_id)
        return self._create_refresh_token(builder, client_id, user_id)

    def _create_refresh_token(self, builder: TokenBuilder, client_id: int, user_id: int):
        token, *_ = builder.set_expiration_time(60 * 60 * 24 * 30).generate()
        self._replace_refresh_token_in_database(client_id, user_id, token)
        return token

    def _create_access_token(self, builder: TokenBuilder, permissions: List[Permissions]):
        return builder.set_expiration_time(1800)\
            .add_permissions(permissions)\
            .generate()

    def _replace_refresh_token_in_database(self, client_id, user_id, new_refresh_token):
        """
        TODO
        Finds record associated with client id and user id
        Updates actual refresh token with new_refresh_token
        If object was not found: creates a new one
        """

    def _get_associated_user(self, refresh_token):
        # TODO gets user and info from database based on refresh_token
        user_id, permissions, client_id = 'Admin', [], 1111
        return user_id, permissions, client_id

    def revoke_token(self, client_id, user_id):
        # TODO
        # Remove token from the database
        pass
