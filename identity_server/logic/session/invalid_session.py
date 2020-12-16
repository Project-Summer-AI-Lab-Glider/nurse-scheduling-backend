from identity_server.logic.session.common_states import ForbiddenAction
from identity_server.logic.session.session import Session, SessionState


class InvalidSession(Session):
    @property
    def initial_state(self):
        """Returns initial state of session"""
        return ForbiddenAction
