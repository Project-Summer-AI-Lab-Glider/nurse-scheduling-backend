from identity_server.logic.session.session import Session
from identity_server.logic.session.invalid_session import InvalidSession
from django.http.request import HttpRequest


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in cls._instances:
            cls._instances[cls.__name__] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls.__name__]


class SessionManager(metaclass=Singleton):
    _sessions = {}

    def handle(self, request: HttpRequest, session_type: type):
        if not self._is_valid(request):
            return InvalidSession().handle(request)
        session_id = request.COOKIES['session_id']
        session = self._get_session(session_id, session_type)
        result = session.handle(request)
        if session.is_finished:
            self._end_session(session_id)
        return result

    def _is_valid(self, request: HttpRequest):
        # TODO add more sophisticated logic (e.g. check if valid)
        return 'session_id' in request.COOKIES

    def _get_session(self, session_id: HttpRequest, session_type: type) -> Session:
        if not session_id or session_id in self._sessions:
            self._sessions[session_id] = session_type()
        return self._sessions[session_id]

    def _end_session(self, session_id):
        del self._sessions[session_id]
