

from mongodb.Worker import Worker
import identity_server.logic.session.login_session.logged_in_state as lis
from identity_server.logic.token_logic.token_logic import TokenLogic
from django.contrib import messages
from django.http.response import HttpResponse
import identity_server.logic.session.login_session.login_session_context as ctx 
from django.http.request import HttpRequest
import identity_server.logic.session.session as sst 
import json

class WaitingForPermissions(sst.SessionState):
    """
    Session is waiting for user credentials and premissions.
    In case of success - returns code
    In case of failure - returns 403
    """

    def required_request_params(self):
        return [
            'is_accepted',
            'client_id'
        ]

    def _get_request_data(self, request: HttpRequest) -> dict:
        if request.body:
            return json.loads(request.body)

    def unprocessable_entity(self, reason: str, request: HttpRequest):
        assert isinstance(self.session_context, ctx.LoginSessionContext)
        scope, app, client_id = self.session_context.scope, self.session_context.app, self.session_context.user_id
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app, 'clientId': client_id})

    def process_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        assert isinstance(self.session_context, ctx.LoginSessionContext)

        client_id, is_accepted = [self._get_request_data(request)[key] for key in [
            'client_id', 'is_accepted']]

        if not is_accepted:
            return self.forbidden_action(json.dumps({'callback_url': f'{self.session_context.callback_url}', 'reason': 'User denied access'}))

        user_id = self._get_user_id(request)

        if not user_id:
            messages.error(request, "Bad username or password")
            return self.bad_request("Bad username or password")
        permissions = self.session_context.scope
        self.session_context.authorized_clients[client_id] = permissions
        refresh_token = TokenLogic.create_token_code(
            user_id=user_id, client_id=client_id, session_id=self.session_id, permissions=permissions)
        self.set_session_state(lis.LoggedIn)
        return self.ok(json.dumps({'callback_url': f'{self.session_context.callback_url}?code={refresh_token}'}))

    def _get_user_id(self, request: HttpRequest) -> str:
        assert isinstance(self.session_context, ctx.LoginSessionContext)
        if self._is_user_logged_in():
            return self.session_context.user_id
        else:
            return self._get_user_by_credentials(request)

    def _is_user_logged_in(self):
        assert isinstance(self.session_context, ctx.LoginSessionContext)
        return self.session_context.user_id != ''

    def _get_user_by_credentials(self, request):
        name, password = [self._get_request_data(request)[key] for key in [
            'name', 'password']]
        user = Worker.objects.filter(name=name).last()
        if not user or user.password != password:
            return None
        self.session_context.user_id = user.id
        return user.id

