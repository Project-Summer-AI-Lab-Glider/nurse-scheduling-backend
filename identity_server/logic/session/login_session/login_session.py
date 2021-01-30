from identity_server.logic.session.login_session.login_session_context import LoginSessionContext
from identity_server.logic.session.login_session.states import InitialLoginState

from identity_server.logic.session.session import Session


class LoginSession(Session):
    def __init__(self) -> None:
        super().__init__(LoginSessionContext)

    def logout_client(self, client_id):
        assert isinstance(self.context, LoginSessionContext)
        del self.context.authorized_clients[client_id]

    @property
    def initial_state(self):
        return InitialLoginState
