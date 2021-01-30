from identity_server.logic.user_logic.user_logic_exceptions import UserAlreadyExists
import json

from django.http import HttpResponse
from django.http.request import HttpRequest

from identity_server.logic.token_logic.token_decoder import TokenDecoder
from identity_server.logic.user_logic.user_logic import User, UserLogic
from identity_server.logic.validation_chain.endpoint_decorator import (
    HttpMethod, Permissions, endpoint)


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
def update_or_delete_user(request: HttpRequest, user_id, **kwargs) -> HttpResponse:
    if request.method == HttpMethod.PUT.value:
        user = json.loads(request.body)
        UserLogic.update_user(user)
        return HttpResponse(status=200, content=json.dumps(user))
    elif request.method == HttpMethod.DELETE.value:
        UserLogic.delete_user(user_id)
        return HttpResponse(status=200)
