import identity_server.logic.session.login_session.logged_in_state as lst
import identity_server.logic.session.login_session.waiting_for_permission as wfp

from mongodb.Application import Application
from mongodb.ApplicationAccount import ApplicationAccount
from django.http.response import HttpResponse
import identity_server.logic.session.login_session.login_session_context as ctx
from typing import Type, Union
from django.http.request import HttpRequest
import identity_server.logic.session.session as ssn


class InitialLoginState(ssn.SessionState):
    """
    Session was not started.
    Checks is request is valid, returns login page in case if yes and bad request otherwise.
    """

    def required_request_params(self):
        return [
            'callback_url',
            'client_id'
        ]

    def route(self, request: HttpRequest) -> Union[Type[ssn.SessionState], None]:
        assert isinstance(self.session_context, ctx.LoginSessionContext)
        data = self._get_request_data(request)
        client_id = data['client_id']
        app = self.get_authorized_app(client_id)
        if app:
            self.session_context.authorized_clients[client_id] = app[0].permissions
            return lst.LoggedIn
        return super().route(request)

    def process_request(self, request: HttpRequest, **kwargs) -> HttpResponse:
        assert isinstance(self.session_context, ctx.LoginSessionContext)
        data = self._get_request_data(request)
        client_id = data['client_id']
        scope, app_name = self._get_app_info(client_id)
        is_logged_in = self.is_user_logged_in()
        self.session_context.assign(
            {'scope': scope, 'callback_url': data['callback_url'], 'client_id': client_id, 'app': app_name})

        self.set_session_state(wfp.WaitingForPermissions)
        return self.render_html(request, 'login_page.html', context={'scope': scope, 'app': app_name, 'clientId': client_id,  'is_logged_in': is_logged_in})

    def is_user_logged_in(self):
        assert isinstance(self.session_context, ctx.LoginSessionContext)
        return self.session_context.user_id != ''

    def get_authorized_app(self, client_id):
        assert isinstance(self.session_context, ctx.LoginSessionContext)
        user_id = self.session_context.user_id
        if user_id:
            authorized_app = ApplicationAccount.objects.filter(
                worker_id=user_id, client_id=client_id)
            return authorized_app

    def _get_app_info(self, client_id) -> Application:
        """
        Makes request to the database to get actual application name associated with given client id
        """
        app = Application.objects.filter(client_id=client_id).first()
        return app.permissions, app.name
