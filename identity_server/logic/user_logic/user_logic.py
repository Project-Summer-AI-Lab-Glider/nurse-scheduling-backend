import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List

from django.core import serializers
from mongodb.Worker import Worker
from mongodb.WorkerShift import WorkerShift


@dataclass
class User:
    name: str
    surname: str
    password: str
    work_type: str
    work_norm: str
    phone_number: int
    id: str = None

    @classmethod
    def required_fields(cls) -> List[str]:
        all_fields = cls.__dataclass_fields__.values()
        return [field.name for field in all_fields if field.default is not None]

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'User':
        native_args = {}
        for name, val in kwargs.items():
            if name in cls.__annotations__:
                native_args[name] = val
        return User(**native_args)


class UserLogic:
    def __init__(self) -> None:
        super().__init__()

    def get_contact(self, user_id):
        worker = Worker.objects.get(id=user_id)
        return json.dumps(self._extract_contact_data(worker))

    def get_contacts(self):
        workers = Worker.objects.all()
        return json.dumps([self._extract_contact_data(worker) for worker in workers])

    def _extract_contact_data(self, worker: Worker):
        return {
            'workerId': worker.id,
            'name': worker.name,
            'phoneNumber': worker.phone_number,
            'surname': worker.surname,
    
        }

    def get_all_users(self):
        all_workers = Worker.objects.all()
        all_workers_json = self._serialize_object(all_workers)
        for worker_dict in all_workers_json:
            worker_dict.pop('password', None)
        return json.dumps(all_workers_json)

    def get_user(self, user_id) -> dict:
        worker = Worker.objects.get(id=user_id)
        worker_dict = self._serialize_object([worker])[0]
        worker_dict.pop('password', None)
        return {**worker_dict, 'id': worker.id}

    def create_user(self, user: User):
        worker = Worker.objects.create(**asdict(user))
        user.id = worker.id

    def get_worker_shift(self, worker_id: int, fromDate: datetime, toDate: datetime):
        workers_shifts = WorkerShift.objects.filter(
            id=worker_id, day__range=(fromDate, toDate))
        # workers_shifts = workers_shifts.filter()
        worker_shift_json = self._serialize_object(workers_shifts)
        return json.dumps(worker_shift_json)

    def create_worke_shift(self, worker_shift: WorkerShift):
        WorkerShift.objects.create(vars(worker_shift))

    def _serialize_object(self, querySet: List[Worker]):
        serializedJson = serializers.serialize("json", querySet)
        jsonObj = json.loads(serializedJson)
        filteredJsonObj = [o['fields'] for o in jsonObj]
        return filteredJsonObj
