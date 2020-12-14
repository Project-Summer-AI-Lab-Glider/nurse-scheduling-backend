from identity_server.logic.session.session import SessionState
from django.http.response import HttpResponse, HttpResponseForbidden


class ForbiddenAction(SessionState):
    def process_request(self, request) -> HttpResponse:
        self.end_session()
        return HttpResponseForbidden("<h1>Action is not allowed</h1>")
