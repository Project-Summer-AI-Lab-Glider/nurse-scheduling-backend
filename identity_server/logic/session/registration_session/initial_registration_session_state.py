from identity_server.logic.user_logic.user_logic import User
from identity_server.logic.session.registration_session.waiting_for_user_data import WaitingForRegistrationData
from identity_server.logic.session.session import SessionState


class InitialRegistrationSessionState(SessionState):

    def process_request(self, request):
        self.set_session_state(WaitingForRegistrationData)
        return self.render_html(request, 'registration_page.html', {'required_fields': User.required_fields()})
