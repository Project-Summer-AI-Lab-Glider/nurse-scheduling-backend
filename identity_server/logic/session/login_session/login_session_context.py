from dataclasses import field, dataclass
from typing import List
from identity_server.logic.session.session import SessionContext


@dataclass
class LoginSessionContext(SessionContext):
    app: str = ''
    scope: List[str] = field(default_factory=list)
    callback_url: str = ''
    user_id: str = ''
    authorized_clients = {}
