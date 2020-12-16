from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Dict, ItemsView, Type
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from dataclasses import dataclass


class ParamsContainer(Enum):
    QueryString = 'query string'
    RequestBody = 'request body'


@dataclass
class SessionContext:
    def assign(self, attributes: dict):
        for key, item in attributes.items():
            setattr(self, key, item)


class SessionState(ABC):
    def __init__(self, set_session_state, get_context, end_session) -> None:
        self.end_session = end_session
        self.set_session_state = set_session_state
        self.session_context = get_context

    @property
    def required_request_params(self) -> Dict[str, type]:
        return ParamsContainer.RequestBody, {}

    def handle(self, request: HttpRequest) -> HttpResponse:
        request_errors = self._validate_request_body(request)
        if request_errors:
            return self.unprocessable_entity(request_errors)
        return self.process_request(request)

    def _validate_request_body(self, request: HttpRequest):
        request_erros = ''
        param_container, required_params = self.required_request_params
        if param_container == ParamsContainer.QueryString:
            actual_params = request.GET
        else:
            actual_params = request.POST
        for required_field, required_type in required_params:
            if required_field not in actual_params:
                request_erros += f'Missing value for field {required_field}'
            if not isinstance(actual_params[required_field], required_type):
                request_erros += f'Bad type for field {required_field}. Exp {required_type}, act: {type(actual_params[required_field])}'
        return request_erros

    @abstractmethod
    def process_request(self, request):
        """
        Processes request and returns expected value
        """

    def unprocessable_entity(self, reason: str):
        self.end_session()
        return HttpResponse(status=422, content_type='text/html', content=f'<h1>{reason}</h1>')

    def render_html(self, request: HttpRequest, template, context):
        return render(request=request, template_name=template, context=context)

    def redirect(self, to, **params):
        return redirect(to, **params)

    def forbidden_action(self, reason=''):
        return HttpResponseForbidden(reason=reason)


class Session(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.is_finished = False
        self._context = SessionContext()
        self.enter_state(self.initial_state)

    def enter_state(self, state: SessionState, **kwargs):
        self._current_state = state(set_session_state=self.enter_state, get_context=self.context,
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

    def handle(self, request) -> HttpResponse:
        """
        Handles reuqest depending on actual session state
        """
        return self._current_state.handle(request)
