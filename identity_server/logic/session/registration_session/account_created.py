from identity_server.logic.session.session import SessionState
import json


class AccountCreated(SessionState):
    def process_request(self, request):
        return json.dumps({'is_created': True})
