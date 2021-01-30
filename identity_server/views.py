from mongodb.ApplicationAccount import ApplicationAccount
from mongodb.Application import Application
from identity_server.logic.session.session import Session
from identity_server.logic.user_logic.user_logic_exceptions import UserAlreadyExists
from django.http.response import HttpResponseForbidden
from identity_server.logic.token_logic.token_logic_exeptions import RefreshTokenNotBelongsToAnyUser
import json

from django.http import HttpResponse
from django.http.request import HttpRequest
from mongodb.Worker import Worker
from mongodb.WorkerShift import WorkerShift

from identity_server.logic.session.login_session import LoginSession
from identity_server.logic.session.registration_session.registration_session import \
    RegistrationSession
from identity_server.logic.session_manager import SessionManager
from identity_server.logic.token_logic.token_builder import TokenType
from identity_server.logic.token_logic.token_decoder import TokenDecoder
from identity_server.logic.token_logic.token_logic import TokenLogic
from identity_server.logic.user_logic.user_logic import User, UserLogic
from identity_server.logic.validation_chain.endpoint_decorator import (
    HttpMethod, Permissions, endpoint)

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


# Resource server

@endpoint(HttpMethod.GET, permissions=[Permissions.CONTACTS_READ])
def get_contacts(request, **kwargs):
    contacts = UserLogic.get_contacts()
    return HttpResponse(contacts)


@endpoint(HttpMethod.GET, permissions=[Permissions.USER_CONTACTS_READ])
def get_user_contacts(request: HttpRequest, user_id, **kwargs):
    contacts = UserLogic.get_contact(user_id)
    return HttpResponse(contacts)


@endpoint(HttpMethod.GET, permissions=[Permissions.ALL_USERS_READ, Permissions.CONTACTS_READ])
def get_users(request: HttpRequest, **kwargs):
    users = UserLogic.get_all_users()
    return HttpResponse(users)


@endpoint(HttpMethod.GET, permissions=[Permissions.CONTACTS_READ])
def get_user(request: HttpRequest, token, **kwargs):
    user_id = TokenDecoder.decode(token)['payload'].setdefault('userId', None)
    user = UserLogic.get_user(user_id)
    return HttpResponse(json.dumps(user))


@endpoint(HttpMethod.POST, permissions=[Permissions.USER_ADD])
def create_user(request: HttpRequest, **kwargs):
    user_data = json.loads(request.body)
    try:
        UserLogic.create_user(User.from_kwargs(**user_data))
    except UserAlreadyExists:
        return HttpResponse(status=409, content="User already exists")
    return HttpResponse(json.dumps('success'))


@endpoint(HttpMethod.GET, permissions=[Permissions.USER_SHIFTS_READ])
def get_workers_shift(request: HttpRequest, user_id, **kwargs):
    fromDate = request.GET.get('from', '')
    toDate = request.GET.get('to', '')
    worker_shifts = UserLogic.get_worker_shift(user_id, fromDate, toDate)
    return HttpResponse(worker_shifts)


@endpoint(HttpMethod.PUT, HttpMethod.DELETE, permissions=[])
def update_or_delete_user(request: HttpRequest, user_id) -> HttpResponse:
    if request.method == HttpMethod.PUT.value:
        user = json.loads(request.body)
        UserLogic.update_user(user)
        return HttpResponse(status=200, content=json.dumps(user))
    elif request.method == HttpMethod.DELETE.value:
        UserLogic.delete_user(user_id)
        return HttpResponse(status=200)

# Server monitoring


@endpoint(HttpMethod.GET)
def is_active(self, **kwargs):
    return HttpResponse(json.dumps({'is_active': True}))

# @endpoint(HttpMethod.POST)
# def revoke_user_access(self, user_id, **kwargs):
# TODO revokes tokens for user with given id
