from typing import List, Tuple

from identity_server.logic.token_logic.token_builder import (TokenBuilder,
                                                             TokenType)
from identity_server.logic.token_logic.token_encoder import TokenEncoder
from identity_server.logic.validation_chain.endpoint_decorator import \
    Permissions
from mongodb.Application import Application
from mongodb.ApplicationAccount import ApplicationAccount


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
        rotated_refresh_token = self.create_refresh_token(
            client_id, user_id, permissions, builder)
        access_token, token_type, seconds_to_expire = self._create_access_token(
            builder, permissions)
        return access_token, token_type, seconds_to_expire, rotated_refresh_token

    def create_refresh_token(self, user_id, client_id, permissions: List[Permissions], builder=None) -> str:
        """
        Creates new refresh token for user with given id and refresh token
        """
        if not builder:
            builder = TokenBuilder(user_id)
        token, *_ = builder.set_expiration_time(60 * 60 * 24 * 30).generate()
        self._replace_or_create_refresh_token_in_database(
            client_id, user_id, token, permissions)
        return token

    def _create_access_token(self, builder: TokenBuilder, permissions: List[Permissions]):
        print(permissions)
        return builder.set_expiration_time(1800)\
            .add_permissions(permissions)\
            .generate()

    def _replace_or_create_refresh_token_in_database(self, client_id: int, user_id: int, new_refresh_token: str, permissions: List[Permissions]):
        try:
            account = ApplicationAccount.objects.get(
                client_id=client_id, worker_id=user_id)
        except ApplicationAccount.DoesNotExist:
            account = ApplicationAccount(
                client_id=client_id, worker_id=user_id, permissions=permissions)
        account.refresh_token = new_refresh_token
        account.permissions=permissions
        account.save()

    def _get_associated_user(self, refresh_token):
        try:
            account = ApplicationAccount.objects.get(
                refresh_token=refresh_token)
        except ApplicationAccount.DoesNotExist:
            raise Exception("No user account exists")
        user_id, permissions, client_id = account.worker_id, account.permissions, account.client_id
        return user_id, permissions, client_id

    def revoke_token(self, client_id, user_id):
        try:
            account = ApplicationAccount.objects.get(
                client_id=client_id, worker_id=user_id)
            account.delete()
        except ApplicationAccount.DoesNotExist:
            pass
