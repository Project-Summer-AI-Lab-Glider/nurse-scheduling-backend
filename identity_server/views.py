from django.http.response import Http404, HttpResponseForbidden
from identity_server.logic.token_logic.token_logic import TokenLogic
from identity_server.logic.user_logic.user_logic import UserLogic
from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse


def login(request):
    return render(request, 'login_page.html')


def get_user_info(request):
    id = 1
    user_info = UserLogic(id).get_user_info()
    return HttpResponse(user_info)


def create_token(request):
    code = 'SDA'  # code that was previously given to app
    encoded_token = TokenLogic().create_token(code)
    return HttpResponse(encoded_token)


def refresh_token(request):
    refreshed_token = TokenLogic().refresh_token()
    return HttpResponse(refresh_token)


def revoke_token(request):
    is_success, token = TokenLogic().revoke_token()
    if is_success:
        return HttpResponse(token)
    else:
        return HttpResponseForbidden()


def introspect_token(request):
    return Http404()
