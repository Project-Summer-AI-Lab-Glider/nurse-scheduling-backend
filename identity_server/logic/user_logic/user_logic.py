class UserLogic:
    def __init__(self, id) -> None:
        super().__init__()
        self._id = id

    def get_user_info(self):
        return {
            'id': self._id,
            'username': 'Alice',
            'phone number': '3123123123',
        }
