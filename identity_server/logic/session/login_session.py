from identity_server.logic.session.common_states import LoggedIn
import json
from dataclasses import asdict, dataclass, field
from typing import List

from mongodb.Worker import Worker
from mongodb.ApplicationAccount import ApplicationAccount
from mongodb.Application import Application

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from identity_server.logic.session.session import (Session, SessionContext,
                                                   SessionState)
from identity_server.logic.token_logic.token_logic import TokenLogic
from mongodb.ApplicationAccount import ApplicationAccount
from mongodb.Worker import Worker


@dataclass
class LoginSessionContext(SessionContext):
    app: str = ''
    scope: List[str] = field(default_factory=list)
    callback_url: str = ''
    client_id: str = ''
    user_id: str = ''


class LoginSession(Session):
    def __init__(self) -> None:
        super().__init__(LoginSessionContext)

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

    def process_request(self, request: HttpRequest) -> HttpResponse:
        assert isinstance(
            self.session_context,
            LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"
        data = self._get_request_data(request)
        client_id = data['client_id']
        app = self._get_app(client_id)
        scope = app.permissions
        app_name = app.name
        self.session_context.assign(
            {'scope': scope, 'callback_url': data['callback_url'], 'client_id': client_id, 'app': app})

        self.set_session_state(WaitingForPermissions)
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app_name, 'clientId': client_id})

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
        assert isinstance(
            self.session_context,
            LoginSessionContext), f"Expected context to be {LoginSessionContext.name}, but actual is {type(self.session_context).name}"
        scope, app, client_id = self.session_context.scope, self.session_context.app, self.session_context.client_id
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app, 'clientId': client_id})

    def process_request(self, request: HttpRequest) -> HttpResponse:
        assert isinstance(
            self.session_context,
            LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"

        client_id = self._get_request_data(request)['client_id']
        user_id = self._validate_user_credentials(request)
        if not user_id:
            return self.bad_request("Bad username or password")
        refresh_token = TokenLogic().create_refresh_token(
            user_id, client_id, self.session_context.scope)
        self.set_session_state(LoggedIn)
        return self.ok(json.dumps({'callback_url': f'{self.session_context.callback_url}?code={refresh_token}'}))

    def _validate_user_credentials(self, request):
        name, password = [self._get_request_data(request)[key] for key in [
            'name', 'password']]
        user = Worker.objects.filter(name=name).last()
        if not user or user.password != password:
            return None
        self.session_context.user_id = user.id
        return user.id


class LoggedIn(SessionState):
    def process_request(self, request):
        # TODO: we do not handle different permissions for different apps. Once you had logged
        # in and get your token you will go everywhere with it
        assert isinstance(
            self.session_context, LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"

        user_id, client_id, callback_url, permissions = [asdict(self.session_context)[key] for key in [
            'user_id', 'client_id', 'scope', 'permissions']]
        refresh_token = TokenLogic().create_refresh_token(user_id, client_id, permissions)

        scope = {'redirect': f'{callback_url}?code={refresh_token}'}
        return self.render_html(request, 'redirect.html', scope)
