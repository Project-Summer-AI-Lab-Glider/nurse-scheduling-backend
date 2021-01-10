from identity_server.logic.session.common_states import LoggedIn
import json
from dataclasses import dataclass, field
from typing import List

from mongodb.Worker import Worker
from mongodb.ApplicationAccount import ApplicationAccount
from mongodb.Application import Application

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from identity_server.logic.session.session import (Session, SessionContext,
                                                   SessionState)


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
        client_id = data['client_id']
        app = self._get_app(client_id)
        scope = app.permissions
        app_name = app.name
        self.session_context.assign(
            {'scope': scope, 'callback_url': data['callback_url'], 'clientId': client_id})
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

    def unprocessable_entity(self, reason: str):
        self.set_session_state(InitialLoginState)
        return super().unprocessable_entity(reason)

    def process_request(self, request: HttpRequest) -> HttpResponse:
        assert isinstance(
            self.session_context, LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"
        client_id = self._get_request_data(request)['client_id']
        name = self._get_request_data(request)['name']
        password = self._get_request_data(request)['password']
        code = self._generate_code()
        worker = Worker.objects.filter(name=name, password=password).last()
        if not worker:
            return self.bad_request("Bad username or password")
        self._save_to_database(code, client_id, worker.id,
                               self.session_context.scope)
        self.set_session_state(LoggedIn)
        return self.ok(json.dumps({'callback_url': f'{self.session_context.callback_url}?code={code}'}))

    def _generate_code(self):
        # TODO DB
        return 'CODE'

    def _save_to_database(self, code, client_id, worker_id, scope):
        # TODO DB DONE
        ApplicationAccount.objects.create(client_id=client_id, worker_id=worker_id,
                                          permissions=scope)
        print(
            f'Saving {client_id} associated with code: {code} and scope: {scope} to database')
