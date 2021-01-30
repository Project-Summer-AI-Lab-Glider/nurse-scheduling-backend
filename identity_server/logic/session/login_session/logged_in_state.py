import identity_server.logic.session.login_session.initial_login_state as ilst
from typing import Type, Union
from mongodb.Worker import Worker
from identity_server.logic.token_logic.token_logic import TokenLogic
import json
from django.http.response import HttpResponse
from identity_server.logic.session.session import SessionState
from identity_server.logic.session.login_session.login_session_context import LoginSessionContext
from django.http.request import HttpRequest


class LoggedIn(SessionState):

    def required_request_params(self):
        return [
            'callback_url',
            'client_id'
        ]

    def route(self, request: HttpRequest) -> Union[Type['SessionState'], None]:
        assert isinstance(
            self.session_context, LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"
        client_id = self._get_request_data(request)['client_id']
        is_authorized = client_id in self.session_context.authorized_clients
        if not is_authorized:
            return ilst.InitialLoginState
        return super().route(request)

    def process_request(self, request: HttpRequest):
        assert isinstance(self.session_context, LoginSessionContext)
        client_id, callback_url = [self._get_request_data(request)[key] for key in [
            'client_id', 'callback_url']]
        permissions = self.session_context.authorized_clients[client_id]
        user_id = self.session_context.user_id
        refresh_token = TokenLogic.create_token_code(
            user_id, client_id, permissions)
        return self.redirect(request, f'{callback_url}?code={refresh_token}')

    def _logout(self, request: HttpRequest):
        assert isinstance(self.session_context, LoginSessionContext)

        body = json.loads(request.body.decode('utf-8'))
        client_id, user_id = body['client_id'], self.session_context.user_id
        TokenLogic.revoke_token(client_id, user_id)
        del self.session_context.authorized_clients[client_id]
        return HttpResponse(json.dumps({'is_success': True}))
