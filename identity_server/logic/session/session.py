from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from typing import List, Type, Union

from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from identity_server.logic.validation_chain.endpoint_decorator import \
    HttpMethod


@dataclass
class SessionContext:
    def assign(self, attributes: dict):
        for key, item in attributes.items():
            setattr(self, key, item)


class SessionState(ABC):
    def __init__(self, set_session_state, context, end_session) -> None:
        self.end_session = end_session
        self.set_session_state = set_session_state
        self.session_context = context

    @property
    def required_request_params(self) -> List[str]:
        return []

    def route(self, request: HttpRequest) -> Union[Type['SessionState'], None]:
        """
        Executes before `self.handle`. Based on :param request: decides whenewer action
        could be handled by this state or session should transision to another state.
        :returns type of state that should handle this request: 
        """

    def handle(self, request: HttpRequest, **kwargs) -> HttpResponse:
        request_errors = self._validate_request_body(request)
        if request_errors:
            return self.unprocessable_entity(request_errors, request)
        return self.process_request(request, **kwargs)

    def conflict(self, confilcted_item, **kwargs) -> HttpResponse:
        return HttpResponse(status=409, content=confilcted_item)

    def _validate_request_body(self, request: HttpRequest):
        request_erros = ''

        required_params = self.required_request_params
        actual_params = self._get_request_data(request)
        for param in required_params:
            if not actual_params or param not in actual_params:
                request_erros += f'Missing value for field {param}\n'
        return request_erros

    def _get_request_data(self, request: HttpRequest):
        if request.method == HttpMethod.GET.value:
            data = request.GET
        elif request.method == HttpMethod.POST.value:
            data = request.POST
        else:
            raise Exception(f"Unsupported request method {request.method}")
        return data

    def bad_request(self, reason: str) -> HttpResponse:
        return HttpResponse(status=400, content_type="application/json", content=reason)

    @abstractmethod
    def process_request(self, request):
        """
        Processes request and returns expected value
        """

    def unprocessable_entity(self, reason: str, request: HttpRequest):
        return HttpResponse(status=422, content_type='text/html', content=f'<h1>{reason}</h1>')

    def render_html(self, request: HttpRequest, template, context):
        return render(request=request, template_name=template, context=context)

    def ok(self, content: str) -> HttpResponse:
        return HttpResponse(content)

    def forbidden_action(self, reason=''):
        return HttpResponseForbidden(reason=reason)

    def redirect(self, request, url):
        scope = {'redirect': url}
        return self.render_html(request, 'redirect.html', scope)


class Session(ABC):
    def __init__(self, context=SessionContext) -> None:
        super().__init__()
        self.is_finished = False
        self._context = context()
        self.enter_state(self.initial_state)

    def enter_state(self, state: Type[SessionState], **kwargs):
        self._current_state = state(set_session_state=self.enter_state, context=self._context,
                                    end_session=self._end_session, **kwargs)

    def _end_session(self):
        self.is_finished = True

    @property
    @abstractmethod
    def initial_state(self) -> Type[SessionState]:
        """Returns initial state of session"""

    @property
    def context(self) -> SessionContext:
        return self._context

    def handle(self, request, **kwargs) -> HttpResponse:
        """
        Handles reuqest depending on actual session state
        """
        handler = self._route(request)
        return handler.handle(request, **kwargs)

    def _route(self, request: HttpRequest) -> SessionState:
        destination_state = self._current_state.route(request)
        if destination_state:
            self.enter_state(destination_state)
            self._route(request)
        return self._current_state
