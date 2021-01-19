from identity_server.logic.validation_chain.handler import Handler


class HttpValidator(Handler):
    def __init__(self):
        super().__init__()

    def handle(self, request, permissions, **kwargs):
        token_parts = request.META.setdefault(
            'HTTP_AUTHORIZATION', '').split(' ')

        if len(token_parts) == 2:
            method, token = token_parts
        else:
            method, token = token_parts[0], ''

        if method and token and permissions:
            metadata = {'method': method, 'token': token, 'excepted_permissions': permissions}
            handler_kwargs = {**metadata, **kwargs}
            return metadata, super().handle(**handler_kwargs)
        else:
            raise Exception("Invalid request")
