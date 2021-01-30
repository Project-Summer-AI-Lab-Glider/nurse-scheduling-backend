from django.http.response import HttpResponseForbidden
from identity_server.logic.token_logic.token_logic_exeptions import RefreshTokenNotBelongsToAnyUser
import json

from django.http import HttpResponse
from django.http.request import HttpRequest

from identity_server.logic.session.login_session import LoginSession
from identity_server.logic.session.registration_session.registration_session import \
    RegistrationSession
from identity_server.logic.session_manager import SessionManager
from identity_server.logic.token_logic.token_decoder import TokenDecoder
from identity_server.logic.token_logic.token_logic import TokenLogic
from identity_server.logic.user_logic.user_logic import UserLogic
from identity_server.logic.validation_chain.endpoint_decorator import (
    HttpMethod, endpoint)

# IS

"""
Scenario 1:
    
    - User logged in to applications and adminpanel 
    - User log outs from admin panel 
    - All accesses removed


Scenario 2:                                                              
    
    - User logged in to two applications and to adminpanel 
    - User revokes token for one of applications from adminpanel level
    - When user reloads application for which token was revoked, application asks him about permissions again

    Handled [V]

Scenario 3:

    - User logged in
    - User token expires
    - Application refereshes user token

    Handled [V]

Scenario 4:

    - User can stop his login process

"""


@endpoint(HttpMethod.GET, HttpMethod.POST)
def login(request: HttpRequest, **kwargs):
    return SessionManager().handle(request, LoginSession)


# TODO frontend should allow to make requests only from adminpanel
# TODO add permission guard
@endpoint(HttpMethod.POST, permissions=[])
def logout(request, token, **kwargs):
    return SessionManager().handle_logout(request, token)


@endpoint(HttpMethod.POST, permissions=[])
def revoke(request, token):
    user_id = TokenDecoder.decode(token)['payload']['userId']
    application_id = json.loads(request.body).setdefault('client_id', None)
    if not application_id:
        return HttpResponse(json.dumps('fail'))
    SessionManager().handle_revoke(request, application_id, user_id)
    return HttpResponse(json.dumps('success'))


@endpoint(HttpMethod.GET, permissions=[])
def get_authorized_apps(request, token, **kwargs):
    user_id = TokenDecoder.decode(token)['payload']['userId']
    return HttpResponse(UserLogic.get_user_authorized_apps(user_id))


@endpoint(HttpMethod.GET, HttpMethod.POST)
def register(request: HttpRequest, **kwargs):
    return SessionManager().handle(request, RegistrationSession)


@endpoint(HttpMethod.GET)
def is_authenticated(request: HttpRequest, **kwargs):
    return SessionManager().handle(request, LoginSession)


@endpoint(HttpMethod.GET)
def create_token(request: HttpRequest, **kwargs):
    refresh_token = request.GET['code']
    try:
        access_token, token_type, seconds_to_expire, rotated_refresh_token = TokenLogic(
        ).create_tokens(refresh_token)
    except RefreshTokenNotBelongsToAnyUser:
        return HttpResponseForbidden(content=f"{refresh_token} is not a valid refresh token")
    return HttpResponse(json.dumps({
        'access_token': access_token,
        'refresh_token': rotated_refresh_token,
        'token_type': token_type.value,
        'expires': seconds_to_expire
    }))


@endpoint(HttpMethod.GET)
def introspect_token(request, token, **kwargs):
    if not token:
        return HttpResponse(status=401, content=json.dumps({'is_authenticated': False}))
    else:
        return HttpResponse(json.dumps({'is_authenticated': True}))
