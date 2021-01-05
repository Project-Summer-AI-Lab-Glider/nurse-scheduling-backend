import json

from django.http import HttpResponse, HttpResponseForbidden
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponseForbidden
from mongodb.Worker import Worker
from mongodb.WorkerShift import WorkerShift

from identity_server.logic.session.login_session import LoginSession
from identity_server.logic.session.registration_session.registration_session import \
    RegistrationSession
from identity_server.logic.session_manager import SessionManager
from identity_server.logic.token_logic.token_logic import TokenLogic
from identity_server.logic.user_logic.user_logic import User, UserLogic
from identity_server.logic.validation_chain.endpoint_decorator import (
    HttpMethod, endpoint)


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
    code = request.GET['code']  # code that was previously given to app
    encoded_token = TokenLogic().create_token(code)
    return HttpResponse(json.dumps({'token': encoded_token}))


@endpoint(HttpMethod.POST)
def refresh_token(request):
    refreshed_token = TokenLogic().refresh_token()
    return HttpResponse(refreshed_token)


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


@endpoint(HttpMethod.GET)
def get_contacts(request):
    contacts = UserLogic().get_contacts()
    return HttpResponse(contacts)


@endpoint(HttpMethod.GET)
def get_user_contacts(request: HttpRequest, user_id):
    contacts = UserLogic().get_contact(user_id)
    return HttpResponse(contacts)


@endpoint(HttpMethod.GET)
def get_users(request: HttpRequest):
    users = UserLogic().get_all_users()
    return HttpResponse(users)


@endpoint(HttpMethod.GET)
def get_user(request: HttpRequest, user_id):
    user = UserLogic().get_user(user_id)
    return HttpResponse(user)


@endpoint(HttpMethod.POST)
def create_user(request: HttpRequest):
    user_data = json.loads(request.body)
    UserLogic().create_user(User.from_kwargs(**user_data))
    return HttpResponse(json.dumps('success'))


@endpoint(HttpMethod.GET)
def get_workers_shift(request: HttpRequest, user_id):
    fromDate = request.GET.get('from', '')
    toDate = request.GET.get('to', '')
    worker_shifts = UserLogic().get_worker_shift(user_id, fromDate, toDate)
    return HttpResponse(worker_shifts)


@endpoint(HttpMethod.POST)
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
