from identity_server.logic.session.registration_session.initial_registration_session_state import InitialRegistrationSessionState
from identity_server.logic.session.session import Session, SessionContext

# class RegistratoinSessoinContext(SessionContext):


class RegistrationSession(Session):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def initial_state(self):
        return InitialRegistrationSessionState
