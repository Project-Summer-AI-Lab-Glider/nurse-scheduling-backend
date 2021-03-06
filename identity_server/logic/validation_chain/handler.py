from __future__ import annotations
from typing import Optional


class Handler:
    def __init__(self, next_item=None):
        self.next_item = next_item
        self._next_handler: Optional[Handler, None] = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    def handle(self, **kwargs) -> bool:
        if self._next_handler:
            return self._next_handler.handle(**kwargs)

        return True
