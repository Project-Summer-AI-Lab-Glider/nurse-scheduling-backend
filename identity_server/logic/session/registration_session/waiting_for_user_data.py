import json

from django.http.request import HttpRequest
from identity_server.logic.session.registration_session.account_created import AccountCreated
from identity_server.logic.session.session import SessionState
from identity_server.logic.user_logic.user_logic import UserLogic, User
from dataclasses import asdict
from identity_server.logic.user_logic.user_logic_exceptions import UserAlreadyExists


class WaitingForRegistrationData(SessionState):

    @property
    def required_request_params(self):
        return User.required_fields()

    def _get_request_data(self, request: HttpRequest) -> dict:
        if request.body:
            return json.loads(request.body)

    def process_request(self, request):
        user_data = self._get_request_data(request)
        new_user = User.from_kwargs(**user_data)
        try:
            UserLogic.create_user(new_user)
        except UserAlreadyExists:
            return self.conflict(new_user)
        finally:
            self.end_session()
        return self.ok(json.dumps(asdict(new_user)))

    def unprocessable_entity(self, reason: str, request: HttpRequest):
        return self.render_html(request, 'registration_page.html', {'required_fields': User.required_fields()})
