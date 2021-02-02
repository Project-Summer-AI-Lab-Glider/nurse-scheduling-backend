from identity_server.logic.session.login_session.initial_login_state import InitialLoginState
import identity_server.logic.session.login_session.login_session_context as ctx

from identity_server.logic.session.session import Session


class LoginSession(Session):
    def __init__(self, **kwargs) -> None:
        super().__init__(context=ctx.LoginSessionContext, **kwargs)

    def logout_client(self, client_id):

        assert isinstance(self.context, ctx.LoginSessionContext)
        if client_id in self.context.authorized_clients:
            del self.context.authorized_clients[client_id]

    @property
    def initial_state(self):
        return InitialLoginState
