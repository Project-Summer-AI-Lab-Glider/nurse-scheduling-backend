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


@endpoint(HttpMethod.GET, HttpMethod.POST)
def login(request: HttpRequest):
    return SessionManager().handle(request, LoginSession)


@endpoint(HttpMethod.GET, HttpMethod.POST)
def register(request: HttpRequest):
    return SessionManager().handle(request, RegistrationSession)


@endpoint(HttpMethod.GET)
def is_authenticated(request: HttpRequest):
    return SessionManager().handle(request, LoginSession)


@endpoint(HttpMethod.GET)
def create_token(request: HttpRequest):
    refresh_token = request.GET['code']
    access_token, token_type, seconds_to_expire, rotated_refresh_token = TokenLogic(
    ).create_tokens(refresh_token)
    return HttpResponse(json.dumps({
        'access_token': access_token,
        'refresh_token': rotated_refresh_token,
        'token_type': token_type.value,
        'expires': seconds_to_expire
    }))


@endpoint(HttpMethod.POST, permissions=[])
def revoke_token(request: HttpRequest):
    return SessionManager().handle_logout(request)


@endpoint(HttpMethod.GET)
def introspect_token(request):
    token = request.META['HTTP_AUTHORIZATION'].strip(TokenType.Bearer.value)
    if not token:
        return HttpResponse(status=401)
    else:
        return HttpResponse(json.dumps({'is_authenticated': True}))


@endpoint(HttpMethod.GET, permissions=[Permissions.CONTACTS_READ])
def get_contacts(request):
    contacts = UserLogic().get_contacts()
    return HttpResponse(contacts)


@endpoint(HttpMethod.GET)
def get_user_contacts(request: HttpRequest, user_id):
    contacts = UserLogic().get_contact(user_id)
    return HttpResponse(contacts)


@endpoint(HttpMethod.GET, permissions=[Permissions.USER_CONTACTS_READ])
def get_user_contacts(request: HttpRequest, user_id):
    contacts = UserLogic().get_contact(user_id)
    return HttpResponse(contacts)


@endpoint(HttpMethod.GET, permissions=[Permissions.ALL_USERS_READ, Permissions.CONTACTS_READ])
def get_users(request: HttpRequest):
    users = UserLogic().get_all_users()
    return HttpResponse(users)


@endpoint(HttpMethod.GET, permissions=[Permissions.CONTACTS_READ])
def get_user(request: HttpRequest):
    token = request.META['HTTP_AUTHORIZATION'].strip(TokenType.Bearer.value)
    user_id = TokenDecoder.decode(token)['payload'].setdefault('userId')
    user = UserLogic().get_user(user_id)
    return HttpResponse(json.dumps(user))


@endpoint(HttpMethod.POST, permissions=[Permissions.USER_ADD])
def create_user(request: HttpRequest):
    user_data = json.loads(request.body)
    UserLogic().create_user(User.from_kwargs(**user_data))
    return HttpResponse(json.dumps('success'))


@endpoint(HttpMethod.GET, permissions=[Permissions.USER_SHIFTS_READ])
def get_workers_shift(request: HttpRequest, user_id):
    fromDate = request.GET.get('from', '')
    toDate = request.GET.get('to', '')
    worker_shifts = UserLogic().get_worker_shift(user_id, fromDate, toDate)
    return HttpResponse(worker_shifts)


@endpoint(HttpMethod.POST, permissions=[Permissions.USER_MOD])
def create_shift(request: HttpRequest, user_id):
    worker_shift = WorkerShift(worker_id=user_id,
                               fromHour=0,
                               toHour=12,
                               code='CODE',
                               name='NAME',
                               isWorking=False,
                               day='2021-01-01')
    UserLogic().create_worke_shift(worker_shift)
    return HttpResponse(json.dumps({'is_success': True}))


@endpoint(HttpMethod.GET)
def is_active(self):
    return HttpResponse(json.dumps({'is_active': True}))
