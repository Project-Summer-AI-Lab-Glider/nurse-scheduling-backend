from identity_server.logic.token_logic.token_logic_exeptions import RefreshTokenNotBelongsToAnyUser
from typing import List, Tuple

from identity_server.logic.token_logic.token_builder import (TokenBuilder,
                                                             TokenType)
from identity_server.logic.validation_chain.endpoint_decorator import \
    Permissions
from mongodb.ApplicationAccount import ApplicationAccount
import uuid


class TokenLogic:
    @staticmethod
    def remove_user_authorized_apps(user_id):
        ApplicationAccount.objects.filter(worker_id=user_id).delete()

    @classmethod
    def create_tokens(cls, refresh_token) -> Tuple[str, TokenType, int, str]:
        """
        Creates new pair of tokens based on refresh token
        """
        user_id, permissions, client_id = cls._get_associated_user(
            refresh_token)
        builder = TokenBuilder(user_id, TokenType.Bearer)
        rotated_refresh_token = cls.create_refresh_token(
            user_id, client_id, permissions, builder)
        access_token, token_type, seconds_to_expire = cls._create_access_token(
            builder, permissions)
        return access_token, token_type, seconds_to_expire, rotated_refresh_token

    @staticmethod
    def create_token_code(user_id, client_id, permissions: List[Permissions]):
        token_code = uuid.uuid4()
        account = ApplicationAccount.objects.filter(
            client_id=client_id, worker_id=user_id)
        if not account:
            account = ApplicationAccount(
                client_id=client_id, worker_id=user_id, permissions=permissions, refresh_token=token_code)
        else:
            account = account[0]
        account.refresh_token = token_code
        account.permissions = permissions
        account.save()
        return token_code

    @classmethod
    def create_refresh_token(cls, user_id, client_id, permissions: List[Permissions], builder) -> str:
        """
        Creates new refresh token for user with given id and refresh token
        """
        token, *_ = builder.set_expiration_time(60 * 60 * 24 * 30).generate()
        cls._replace_refresh_token_in_database(
            client_id, user_id, token, permissions)
        return token

    @staticmethod
    def _create_access_token(builder: TokenBuilder, permissions: List[Permissions]):
        return builder.set_expiration_time(60 * 60 * 2)\
            .add_permissions(permissions)\
            .generate()

    @staticmethod
    def _replace_refresh_token_in_database(client_id: int, user_id: int, new_refresh_token: str, permissions: List[Permissions]):
        try:
            account = ApplicationAccount.objects.get(
                client_id=client_id, worker_id=user_id)
        except ApplicationAccount.DoesNotExist:
            raise RefreshTokenNotBelongsToAnyUser(client_id)
        account.refresh_token = new_refresh_token
        account.permissions = permissions
        account.save()

    @staticmethod
    def _get_associated_user(refresh_token):
        try:
            account = ApplicationAccount.objects.get(
                refresh_token=refresh_token)
        except ApplicationAccount.DoesNotExist:
            raise RefreshTokenNotBelongsToAnyUser()
        user_id, permissions, client_id = account.worker_id, account.permissions, account.client_id
        return user_id, permissions, client_id

    @staticmethod
    def revoke_token(client_id, user_id):
        try:
            account = ApplicationAccount.objects.get(
                client_id=client_id, worker_id=user_id)
            account.delete()
        except ApplicationAccount.DoesNotExist:
            pass
