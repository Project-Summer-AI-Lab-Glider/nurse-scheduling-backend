
from identity_server.logic.token_logic.token_decoder import TokenDecoder
from identity_server.logic.session.revoked_token_provider import RevokedTokenProvider
from identity_server.logic.session.singleton import Singleton
from identity_server.logic.user_logic.user_logic import UserLogic
import json
import uuid

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from identity_server.logic.session.login_session import LoginSession
from identity_server.logic.session.session import Session
from identity_server.logic.token_logic.token_logic import TokenLogic


class SessionManager(metaclass=Singleton):
    _sessions = {}
    session_id_cookie = 'session'

    def end_session(self, request: HttpRequest, session_type: type):
        cookie_name = f'{self.session_id_cookie}_{session_type.__name__}'
        session_id = request.COOKIES[cookie_name]
        if session_id:
            self._end_session(session_id)

    def handle(self, request: HttpRequest, session_type: type, **kwargs):
        cookie_name = f'{self.session_id_cookie}_{session_type.__name__}'
        session_id = request.COOKIES.setdefault(
            cookie_name, self._create_session_id())

        session = self._get_session(session_id, session_type)
        result = session.handle(request, **kwargs)
        if session.is_finished:
            self._end_session(session_id)
        result.set_cookie(cookie_name,
                          session_id, max_age=60*60*24*5, secure=False, samesite=False)
        return result

    def handle_revoke(self, request, client_id, user_id):
        """
        Revokes user access from application, 
        but user still logged in
        """
        login_session_key = f'{self.session_id_cookie}_{LoginSession.__name__}'
        session_id = request.COOKIES[login_session_key]
        if session_id in self._sessions:
            session = self._sessions[session_id]
            assert isinstance(session, LoginSession)
            session.logout_client(client_id)
        TokenLogic().revoke_token(client_id, user_id)
        return HttpResponse(json.dumps({'is_success': True}))

    def handle_logout(self, request, token):
        """
        Logs user out of application
        """
        RevokedTokenProvider().add_revoked_token(token)
        user_id = TokenDecoder.decode(token)['payload']['userId']
        TokenLogic.remove_user_authorized_apps(user_id)
        self.end_session(request, LoginSession)
        return HttpResponse(json.dumps({'is_success': True}))

    def _create_session_id(self):
        return uuid.uuid4()

    def _is_valid(self, request: HttpRequest):
        return self.session_id_cookie in request.COOKIES

    def _get_session(self, session_id: str, session_type: type) -> Session:
        if not session_id or session_id not in self._sessions:
            self._sessions[session_id] = session_type()
        return self._sessions[session_id]

    def _end_session(self, session_id):
        if session_id in self._sessions:
            del self._sessions[session_id]
