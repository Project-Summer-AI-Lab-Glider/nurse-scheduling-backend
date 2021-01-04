from identity_server.logic.session.registration_session.account_created import AccountCreated
from identity_server.logic.session.session import SessionState
from identity_server.logic.user_logic.user_logic import UserLogic, User
from dataclasses import asdict


class WaitingForRegistrationData(SessionState):

    @property
    def required_request_params(self):
        return User.__dataclass_fields__.keys()

    def process_request(self, request):
        user_data = self._get_request_data(request)
        new_user = User(**user_data)
        UserLogic().create_user(new_user)
        self.set_session_state(AccountCreated)
        return self.ok(asdict(new_user))
