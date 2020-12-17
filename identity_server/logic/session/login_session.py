from functools import partial
from identity_server.logic.endpoint_decorator import endpoint
from typing import Callable, List
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from identity_server.logic.session.session import Session, SessionContext, SessionState
from dataclasses import dataclass, field
import json


@dataclass
class LoginSessionContext(SessionContext):
    scope: List[str] = field(default_factory=list)
    callback_url: str = ''
    client_id: str = ''


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
            'scope',
            'callback_url',
            'client_id'
        ]

    def process_request(self, request: HttpRequest) -> HttpResponse:
        assert isinstance(
            self.session_context, LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"
        data = self._get_request_data(request)
        scope = data['scope'].split(",")
        client_id = data['client_id']
        self.session_context.assign(
            {'scope': scope, 'callback_url': data['callback_url'], 'clientId': client_id})
        app = self._get_app(client_id)
        self.set_session_state(WaitingForPermissions)
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app, 'clientId': client_id})

    def _get_app(self, client_id):
        """
        Makes request t oa database to get a name of an app
        """
        return 'App'


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

    def process_request(self, request: HttpRequest) -> HttpResponse:
        assert isinstance(
            self.session_context, LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"
        client_id = self._get_request_data(request)['client_id']
        code = self._generate_code()
        self._save_to_database(code, client_id, self.session_context.scope)
        return self.redirect(self.session_context.callback_url, code=code)

    def _generate_code(self):
        # TODO Add logic
        return 'CODE'

    def _save_to_database(self, code, client_id, scope):
        # TODO Add logic
        print(
            f'Saving {client_id} associated with code: {code} and scope: {scope} to database')
