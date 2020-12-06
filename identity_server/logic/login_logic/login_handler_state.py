from abc import ABC, abstractmethod


class LoginHandlerState(ABC):
    @abstractmethod
    def handle(self, request):
        """
        Handles reuqest depending on actual login session state
        """


class WaitingForLoginRequest(LoginHandlerState):
    def handle(self, request):
        pass


class WaitingForCredentials(LoginHandlerState):
    def handle(self, request):
        pass
