from mongodb.ApplicationAccount import ApplicationAccount
from typing import Type, Union
from mongodb.Worker import Worker
from identity_server.logic.token_logic.token_logic import TokenLogic
from django.contrib import messages
import json
from django.http.response import HttpResponse
from identity_server.logic.session.session import SessionState
from identity_server.logic.session.login_session.login_session_context import LoginSessionContext
from django.http.request import HttpRequest
from mongodb.Application import Application


class InitialLoginState(SessionState):
    """
    Session was not started.
    Checks is request is valid, returns login page in case if yes and bad request otherwise.
    """

    @property
    def required_request_params(self):
        return [
            'callback_url',
            'client_id'
        ]

    def route(self, request: HttpRequest) -> Union[Type['SessionState'], None]:
        assert isinstance(self.session_context, LoginSessionContext)
        data = self._get_request_data(request)
        client_id = data['client_id']
        app = self.get_authorized_app(client_id)
        if app:
            self.session_context.authorized_clients[client_id] = app[0].permissions
            return LoggedIn
        return super().route(request)

    def process_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        assert isinstance(self.session_context, LoginSessionContext)
        data = self._get_request_data(request)
        client_id = data['client_id']
        app = self._get_app(client_id)
        scope = app.permissions
        app_name = app.name
        is_logged_in = self.is_user_logged_in()
        self.session_context.assign(
            {'scope': scope, 'callback_url': data['callback_url'], 'client_id': client_id, 'app': app_name})

        self.set_session_state(WaitingForPermissions)
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app_name, 'clientId': client_id,  'is_logged_in': is_logged_in})

    def is_user_logged_in(self):
        assert isinstance(self.session_context, LoginSessionContext)
        return self.session_context.user_id != ''

    def get_authorized_app(self, client_id):
        assert isinstance(self.session_context, LoginSessionContext)
        user_id = self.session_context.user_id
        if user_id:
            authorized_app = ApplicationAccount.objects.filter(
                worker_id=user_id, client_id=client_id)
            return authorized_app

    def _get_app(self, client_id) -> Application:
        """
        Makes request to the database to get actual application name associated with given client id
        """

        result = Application.objects.filter(client_id=client_id).first()
        return result


class LoggedIn(SessionState):
    @property
    def required_request_params(self):
        return [
            'callback_url',
            'client_id'
        ]

    def route(self, request: HttpRequest) -> Union[Type['SessionState'], None]:
        assert isinstance(
            self.session_context, LoginSessionContext), f"Expected context to be {LoginSessionContext.__name__}, but actual is {type(self.session_context).__name__}"
        client_id = self._get_request_data(request)['client_id']
        is_authorized = client_id in self.session_context.authorized_clients
        if not is_authorized:
            return InitialLoginState
        return super().route(request)

    def process_request(self, request: HttpRequest):
        assert isinstance(self.session_context, LoginSessionContext)
        client_id, callback_url = [self._get_request_data(request)[key] for key in [
            'client_id', 'callback_url']]
        permissions = self.session_context.authorized_clients[client_id]
        user_id = self.session_context.user_id
        refresh_token = TokenLogic().create_token_code(user_id, client_id, permissions)
        return self.redirect(request, f'{callback_url}?code={refresh_token}')

    def _logout(self, request: HttpRequest):
        assert isinstance(self.session_context, LoginSessionContext)

        body = json.loads(request.body.decode('utf-8'))
        client_id, user_id = body['client_id'], self.session_context.user_id
        TokenLogic().revoke_token(client_id, user_id)
        del self.session_context.authorized_clients[client_id]
        return HttpResponse(json.dumps({'is_success': True}))


class WaitingForPermissions(SessionState):
    """
    Session is waiting for user credentials and premissions.
    In case of success - returns code
    In case of failure - returns 403
    """

    @property
    def required_request_params(self):
        return [
            'is_accepted',
            'client_id'
        ]

    def _get_request_data(self, request: HttpRequest) -> dict:
        if request.body:
            return json.loads(request.body)

    def unprocessable_entity(self, reason: str, request: HttpRequest):
        assert isinstance(self.session_context, LoginSessionContext)
        scope, app, client_id = self.session_context.scope, self.session_context.app, self.session_context.user_id
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app, 'clientId': client_id})

    def process_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        assert isinstance(self.session_context, LoginSessionContext)

        client_id, is_accepted = [self._get_request_data(request)[key] for key in [
            'client_id', 'is_accepted']]
        if not is_accepted:
            return self.forbidden_action(json.dumps({'callback_url': f'{self.session_context.callback_url}', 'reason': 'User denied access'}))

        user_id = self._get_user_id(request)
        if not user_id:
            messages.error(request, "Bad username or password")
            return self.bad_request("Bad username or password")
        permissions = self.session_context.scope
        self.session_context.authorized_clients[client_id] = permissions
        refresh_token = TokenLogic().create_token_code(user_id, client_id, permissions)

        self.set_session_state(LoggedIn)
        return self.ok(json.dumps({'callback_url': f'{self.session_context.callback_url}?code={refresh_token}'}))

    def _get_user_id(self, reuqest: HttpRequest) -> str:
        assert isinstance(self.session_context, LoginSessionContext)
        if self._is_user_logged_in():
            return self.session_context.user_id
        else:
            return self._get_user_by_credentials(reuqest)

    def _is_user_logged_in(self):
        assert isinstance(self.session_context, LoginSessionContext)
        return self.session_context.user_id != ''

    def _get_user_by_credentials(self, request):
        name, password = [self._get_request_data(request)[key] for key in [
            'name', 'password']]
        user = Worker.objects.filter(name=name).last()
        if not user or user.password != password:
            return None
        self.session_context.user_id = user.id
        return user.id
