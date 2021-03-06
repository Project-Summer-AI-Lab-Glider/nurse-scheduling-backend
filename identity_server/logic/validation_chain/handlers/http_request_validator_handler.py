from identity_server.logic.validation_chain.handler import Handler
from identity_server.logic.validation_chain.exceptions.validator_exceptions import HTTPRequestValidatorException


class HttpRequestValidator(Handler):
    def __init__(self):
        super().__init__()

    def handle(self, request, permissions, **kwargs):
        token_parts = request.META.setdefault(
            'HTTP_AUTHORIZATION', '').split(' ')

        if len(token_parts) == 2:
            method, token = token_parts
        else:
            method, token = token_parts[0], ''

        if method is not None and token is not None:
            metadata = {'method': method, 'token': token, 'excepted_permissions': permissions}
            handler_kwargs = {**metadata, **kwargs}
            return super().handle(**handler_kwargs)
        else:
            raise HTTPRequestValidatorException()
