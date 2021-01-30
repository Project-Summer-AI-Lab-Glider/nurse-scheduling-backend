from identity_server.logic.token_logic.token_logic_exeptions import RefreshTokenNotBelongsToAnyUser
from typing import List, Tuple

from identity_server.logic.token_logic.token_builder import (TokenBuilder,
                                                             TokenType)
from identity_server.logic.token_logic.token_encoder import TokenEncoder
from identity_server.logic.validation_chain.endpoint_decorator import \
    Permissions
from mongodb.ApplicationAccount import ApplicationAccount
import uuid


class TokenLogic:
    def __init__(self) -> None:
        self._token_encoder = TokenEncoder()

    def remove_user_authorized_apps(user_id):
        ApplicationAccount.objects.filter(worker_id=user_id).delete()

    def create_tokens(self, refresh_token) -> Tuple[str, TokenType, int, str]:
        """
        Creates new pair of tokens based on refresh token
        """
        # TODO handle multiple requests to DB
        user_id, permissions, client_id = self._get_associated_user(
            refresh_token)
        builder = TokenBuilder(user_id, TokenType.Bearer)
        rotated_refresh_token = self.create_refresh_token(
            user_id, client_id, permissions, builder)
        access_token, token_type, seconds_to_expire = self._create_access_token(
            builder, permissions)
        return access_token, token_type, seconds_to_expire, rotated_refresh_token

    def create_token_code(self, user_id, client_id, permissions: List[Permissions]):
        token_code = uuid.uuid4()
        account = ApplicationAccount(
            client_id=client_id, worker_id=user_id, permissions=permissions, refresh_token=token_code)
        account.save()
        return token_code

    def create_refresh_token(self, user_id, client_id, permissions: List[Permissions], builder) -> str:
        """
        Creates new refresh token for user with given id and refresh token
        """
        token, *_ = builder.set_expiration_time(60 * 60 * 24 * 30).generate()
        self._replace_refresh_token_in_database(
            client_id, user_id, token, permissions)
        return token

    def _create_access_token(self, builder: TokenBuilder, permissions: List[Permissions]):
        return builder.set_expiration_time(60 * 60 * 2)\
            .add_permissions(permissions)\
            .generate()

    def _replace_refresh_token_in_database(self, client_id: int, user_id: int, new_refresh_token: str, permissions: List[Permissions]):
        try:
            account = ApplicationAccount.objects.get(
                client_id=client_id, worker_id=user_id)
        except ApplicationAccount.DoesNotExist:
            raise RefreshTokenNotBelongsToAnyUser(client_id)
        account.refresh_token = new_refresh_token
        account.permissions = permissions
        account.save()

    def _get_associated_user(self, refresh_token):
        try:
            account = ApplicationAccount.objects.get(
                refresh_token=refresh_token)
        except ApplicationAccount.DoesNotExist:
            raise RefreshTokenNotBelongsToAnyUser()
        user_id, permissions, client_id = account.worker_id, account.permissions, account.client_id
        return user_id, permissions, client_id

    def revoke_token(self, client_id, user_id):
        try:
            account = ApplicationAccount.objects.get(
                client_id=client_id, worker_id=user_id)
            account.delete()
        except ApplicationAccount.DoesNotExist:
            pass
