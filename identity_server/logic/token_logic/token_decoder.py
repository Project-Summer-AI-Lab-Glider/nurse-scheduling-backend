import base64


class TokenDecoder:

    @classmethod
    def decode(cls, token: str):
        header_enc, payload_enc, signature_enc = token.split('.')
        payload = cls._base64_decode(payload_enc)
        header = cls._base64_decode(header_enc)
        signature = cls._base64_decode(signature_enc)
        return {'header': header, 'payload': payload, 'signature': signature}

    @staticmethod
    def _base64_decode(statement: str) -> bytes:
        statement += '=' * (-len(statement) % 4)
        return base64.urlsafe_b64decode(statement)
