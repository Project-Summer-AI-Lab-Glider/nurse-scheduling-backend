import json
from dataclasses import asdict, dataclass, field
from typing import List, Type, Union

from django.http import request
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from identity_server.logic.session.common_states import LoggedIn
from identity_server.logic.session.session import (Session, SessionContext,
                                                   SessionState)
from identity_server.logic.token_logic.token_logic import TokenLogic
from mongodb.Application import Application
from mongodb.ApplicationAccount import ApplicationAccount
from mongodb.Worker import Worker


@dataclass
class LoginSessionContext(SessionContext):
    app: str = ''
    scope: List[str] = field(default_factory=list)
    callback_url: str = ''
    user_id: str = ''
    authorized_clients = {}


class LoginSession(Session):
    def __init__(self) -> None:
        super().__init__(LoginSessionContext)

    def logout_client(self, client_id):
        assert isinstance(self.context, LoginSessionContext)
        del self.context.authorized_clients[client_id]

    @property
    def initial_state(self):
        return InitialLoginState


class InitialLoginState(SessionState):
    """
    Session was not started.
    Checks is request is valid, returns login page in case if yes and bad request otherwise.
    """

    @property
    def required_request_params(self):
        return [
            'callback_url',
            'client_id'
        ]

    def process_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        assert isinstance(self.session_context, LoginSessionContext)
        data = self._get_request_data(request)
        client_id = data['client_id']
        app = self._get_app(client_id)
        scope = app.permissions
        app_name = app.name
        is_logged_in = self.is_user_logged_in()
        self.session_context.assign(
            {'scope': scope, 'callback_url': data['callback_url'], 'client_id': client_id, 'app': app})

        self.set_session_state(WaitingForPermissions)
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app_name, 'clientId': client_id,  'is_logged_in': is_logged_in})

    def is_user_logged_in(self):
        assert isinstance(self.session_context, LoginSessionContext)
        return self.session_context.user_id != ''

    def _get_app(self, client_id) -> Application:
        """
        Makes request to the database to get actual application name associated with given client id
        """
        return Application.objects.filter(client_id=client_id).first()


class WaitingForPermissions(SessionState):
    """
    Session is waiting for user credentials and premissions.
    In case of success - returns code
    In case of failure - returns 403
    """

    @property
    def required_request_params(self):
        return [
            'is_accepted',
            'client_id'
        ]

    def _get_request_data(self, request: HttpRequest) -> dict:
        if request.body:
            return json.loads(request.body)

    def unprocessable_entity(self, reason: str, request: HttpRequest):
        assert isinstance(self.session_context, LoginSessionContext)
        client_id = self._get_request_data(request)['client_id']
        scope, app, client_id = self.session_context.scope, self.session_context.app
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app, 'clientId': client_id})

    def process_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        assert isinstance(self.session_context, LoginSessionContext)

        client_id = self._get_request_data(request)['client_id']
        user_id = self._get_user_id(request)
        if not user_id:
            return self.bad_request("Bad username or password")
        permissions = self.session_context.scope
        self.session_context.authorized_clients[client_id] = permissions
        refresh_token = TokenLogic().create_refresh_token(user_id, client_id, permissions)

        self.set_session_state(LoggedIn)
        return self.ok(json.dumps({'callback_url': f'{self.session_context.callback_url}?code={refresh_token}'}))

    def _get_user_id(self, reuqest: HttpRequest) -> str:
        assert isinstance(self.session_context, LoginSessionContext)
        if self._is_user_logged_in():
            return self.session_context.user_id
        else:
            return self._get_user_by_credentials(reuqest)

    def _is_user_logged_in(self):
        assert isinstance(self.session_context, LoginSessionContext)
        return self.session_context.user_id != ''

    def _get_user_by_credentials(self, request):
        name, password = [self._get_request_data(request)[key] for key in [
            'name', 'password']]
        user = Worker.objects.filter(name=name).last()
        if not user or user.password != password:
            return None
        self.session_context.user_id = user.id
        return user.id


class LoggedIn(SessionState):
    @property
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
            return InitialLoginState
        return super().route(request)

    def process_request(self, request, logout=False):
        assert isinstance(self.session_context, LoginSessionContext)
        if logout:
            return self._logout()
        else:
            return self._create_refresh_token()

    def _logout(self):
        assert isinstance(self.session_context, LoginSessionContext)

        body = json.loads(request.body.decode('utf-8'))
        client_id, user_id = body['client_id'], self.session_context.user_id
        TokenLogic().revoke_token(client_id, user_id)
        del self.session_context.authorized_clients[client_id]
        return HttpResponse(json.dumps({'is_success': True}))

    def _create_refresh_token(self):
        client_id, callback_url = [self._get_request_data(request)[key] for key in [
            'client_id', 'callback_url']]
        permissions = self.session_context.authorized_clients[client_id]
        user_id = self.session_context.user_id
        refresh_token = TokenLogic().create_refresh_token(user_id, client_id, permissions)

        scope = {'redirect': f'{callback_url}?code={refresh_token}'}
        return self.render_html(request, 'redirect.html', scope)
