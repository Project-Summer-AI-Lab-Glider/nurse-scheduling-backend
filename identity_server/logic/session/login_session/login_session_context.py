from dataclasses import field, dataclass
from typing import List
from identity_server.logic.session.session import SessionContext
from identity_server.logic.validation_chain.permissions import Permissions


@dataclass
class LoginSessionContext(SessionContext):
    app: str = ''
    scope: List[Permissions] = field(default_factory=list)
    callback_url: str = ''
    user_id: str = ''
    authorized_clients = {}
