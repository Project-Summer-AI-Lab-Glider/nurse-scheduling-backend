from functools import partial
from identity_server.logic.endpoint_decorator import endpoint
from typing import Callable, List
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from identity_server.logic.session.session import ParamsContainer, Session, SessionContext, SessionState
from dataclasses import dataclass, field


@dataclass
class LoginSessionContext(SessionContext):
    scope: List[str] = field(default_factory=list)
    callback_url: str = ''


class LoginSession(Session):
    def __init__(self) -> None:
        super().__init__()
        self._context = LoginSessionContext()

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
        return ParamsContainer.QueryString, {
            'scope': list,
            'callback_url': str,
            'client_id': str
        }

    def process_request(self, request: HttpRequest) -> HttpResponse:
        assert isinstance(self.session_context, LoginSessionContext)
        scope = request.GET['scope']
        self.session_context.assign(
            {'scope': scope, 'callback_url': request.POST.callback_url})
        self.set_session_state(WaitingForPermissions)
        return self.render_html(request, 'identity_server/login_page.htlm', context={'scope': scope})


class WaitingForPermissions(SessionState):
    """
    Session is waiting for user credentials and premissions. 
    In case of success - returns code
    In case of failure - returns 403 
    """
    @property
    def required_request_params(self):
        return ParamsContainer.RequestBody, {
            'is_success': bool,
            'client_id': str
        }

    def process_request(self, request: HttpRequest) -> HttpResponse:
        assert isinstance(self.session_context, LoginSessionContext)
        client_id = request.POST['client_id']
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
