
import binascii
import base64
from identity_server.logic.session.session import Session
from identity_server.logic.session.invalid_session import InvalidSession
from django.http.request import HttpRequest
import uuid


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in cls._instances:
            cls._instances[cls.__name__] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls.__name__]


class SessionManager(metaclass=Singleton):
    _sessions = {}
    session_id_cookie = 'session'

    def handle(self, request: HttpRequest, session_type: type):
        cookie_name = f'{self.session_id_cookie}_{session_type.__name__}'
        session_id = request.COOKIES.setdefault(
            cookie_name, self._create_session_id())

        session = self._get_session(session_id, session_type)
        result = session.handle(request)
        if session.is_finished:
            self._end_session(session_id)
        result.set_cookie(cookie_name,
                          session_id, max_age=60*60*24*5, secure=False, samesite=False)
        return result

    def _create_session_id(self):
        return uuid.uuid4()

    def _is_valid(self, request: HttpRequest):
        return self.session_id_cookie in request.COOKIES

    def _get_session(self, session_id: str, session_type: type) -> Session:
        if not session_id or session_id not in self._sessions:
            self._sessions[session_id] = session_type()
        return self._sessions[session_id]

    def _end_session(self, session_id):
        del self._sessions[session_id]
