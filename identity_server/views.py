import json
from identity_server.logic.session.login_session import LoginSession
from identity_server.logic.session_manager import SessionManager
from identity_server.logic.endpoint_decorator import HttpMethod, endpoint
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponseForbidden
from identity_server.logic.token_logic.token_logic import TokenLogic
from identity_server.logic.user_logic.user_logic import UserLogic
from django.http import HttpResponseForbidden, HttpResponse


@endpoint(HttpMethod.GET, HttpMethod.POST)
def login(request: HttpRequest):
    return SessionManager().handle(request, LoginSession)


@endpoint(HttpMethod.GET)
def is_authenticated(request: HttpRequest):
    return SessionManager().handle(request, LoginSession)


@endpoint(HttpMethod.GET)
def create_token(request: HttpRequest):
    code = request.GET['code']  # code that was previously given to app
    encoded_token = TokenLogic().create_token(code)
    return HttpResponse(json.dumps({'token': encoded_token}))


@endpoint(HttpMethod.GET)
def get_user_info(request):
    id = 1
    user_info = UserLogic(id).get_user_info()
    return HttpResponse(user_info)


@endpoint(HttpMethod.POST)
def refresh_token(request):
    refreshed_token = TokenLogic().refresh_token()
    return HttpResponse(refresh_token)


@endpoint(HttpMethod.POST, HttpMethod.DELETE)
def revoke_token(request):
    is_accepted, token = TokenLogic().revoke_token()
    if is_accepted:
        return HttpResponse(token)
    else:
        return HttpResponseForbidden()


@endpoint(HttpMethod.GET)
def introspect_token(request):
    return Http404()
