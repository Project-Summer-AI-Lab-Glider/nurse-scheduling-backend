import json
from identity_server.logic.session.login_session import LoginSession
from identity_server.logic.session_manager import SessionManager
from identity_server.logic.validation_chain.endpoint_decorator import HttpMethod, endpoint
from django.http.request import HttpRequest
from django.http.response import Http404
from identity_server.logic.token_logic.token_logic import TokenLogic
from identity_server.logic.user_logic.user_logic import UserLogic
from django.http import HttpResponseForbidden, HttpResponse
from mongodb.Worker import Worker
from mongodb.WorkerShift import WorkerShift


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
def get_contacts(request: HttpRequest, user_id):
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
    worker = Worker(worker_id='3', 
                name='Anna',  
                surname='Kowalskowa', 
                work_type='0', 
                work_norm='0',
                phone_number='999-999-999')
    UserLogic().create_user(worker)
    return HttpResponse('success')

#worker_shifts/1?from=2021-01-01&to=2021-01-05
@endpoint(HttpMethod.GET)
def get_workers_shift(request: HttpRequest, user_id):
    fromDate = request.GET.get('from','')
    toDate = request.GET.get('to','')
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
    return HttpResponse('success')
    

# TODO add validation decorator
# TODO add endpoints
# 1. GET contacts
# Returns
#  Worker {
#   workerId: string;
#   name: string;
#   phoneNumber: string;
# }
# 2. GET users
# Returns:
# [Worker {
#   workerId: string;
#   name: string;
#   type: WorkerType;
#   workNorm: number; // 0 - 1
#   phoneNumber: string;
# }]
# 3. GET users/{id}
# Returns
# Worker {
#   workerId: string;
#   name: string;
#   type: WorkerType;
#   workNorm: number; // 0 - 1
#   phoneNumber: string;
# }
# 4. POST user
# Accepts:
# Worker {
#   workerId: string;
#   name: string;
#   type: WorkerType;
#   workNorm: number; // 0 - 1
#   phoneNumber: string;
# }
# 5. GET shifts/{worker_id}?from=yyyy.mm.dd&to=yyyy.mm.dd
# Returns:
# [Shift {
#   fromHour: number; // 0 - 24
#   toHour: number;
#   code: string;
#   name: string;
#   isWorking: boolean;
#   day: number
# }]
#  6. POST shifts/{worker_id}
# [Shift {
#   fromHour: number; // 0 - 24
#   toHour: number;
#   code: string;
#   name: string;
#   isWorking: boolean;
#   day: number
# }]
