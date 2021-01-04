from __future__ import annotations
from abc import abstractmethod
from typing import Any, Optional


class Handler:
    def __init__(self, next_item=None):
        self.next_item = next_item
        self._next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: Any) -> Optional[bool]:
        if self._next_handler:
            return self._next_handler.handle(request)

        return None
