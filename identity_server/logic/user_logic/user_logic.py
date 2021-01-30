from mongodb.Application import Application
from mongodb.ApplicationAccount import ApplicationAccount
from identity_server.logic.user_logic.user_logic_exceptions import UserAlreadyExists, UserNotExists
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
    password: str
    surname: str = ''
    work_type: str = ''
    work_norm: str = ''
    phone_number: int = ''
    id: str = None

    @classmethod
    def required_fields(cls) -> List[str]:
        return ['name', 'password']

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'User':
        native_args = {}
        for name, val in kwargs.items():
            if name in cls.__annotations__:
                native_args[name] = val
        return User(**native_args)


class UserLogic:
    @classmethod
    def delete_user(cls, user_id):
        try:
            user = Worker.objects.get(id=user_id)
            user.delete()
        except Worker.DoesNotExist:
            pass

    @classmethod
    def update_user(cls, new_user_data: User):
        try:
            old_user_data = Worker.objects.get(id=new_user_data.id)
        except Worker.DoesNotExist:
            raise UserNotExists(new_user_data)
        old_user_data.update(**asdict(new_user_data))

    @staticmethod
    def get_user_authorized_apps(user_id):
        apps = Application.objects.all()
        authorized_apps = [
            app.client_id for app in ApplicationAccount.objects.filter(worker_id=user_id)]
        authorized_apps = [{
            'client_id': app.client_id,
            'name': app.name,
        } for app in apps if app.client_id in authorized_apps]
        return json.dumps(authorized_apps)

    @classmethod
    def get_contact(cls, user_id):
        worker = Worker.objects.get(id=user_id)
        return json.dumps(cls._extract_contact_data(worker))

    @classmethod
    def get_contacts(cls):
        workers = Worker.objects.all()
        return json.dumps([cls._extract_contact_data(worker) for worker in workers])

    @staticmethod
    def _extract_contact_data(worker: Worker):
        return {
            'workerId': worker.id,
            'name': worker.name,
            'phoneNumber': worker.phone_number,
            'surname': worker.surname,

        }

    @classmethod
    def get_all_users(cls):
        all_workers = Worker.objects.all()
        all_workers_json = cls._serialize_object(all_workers)
        for serialized_worker, query_result in zip(all_workers_json, all_workers):
            serialized_worker.pop('password', None)
            serialized_worker['id'] = query_result.id
        return json.dumps(all_workers_json)

    @classmethod
    def get_user(cls, user_id) -> dict:
        worker = Worker.objects.get(id=user_id)
        worker_dict = cls._serialize_object([worker])[0]
        worker_dict.pop('password', None)
        return {**worker_dict, 'id': worker.id}

    @staticmethod
    def create_user(new_user: User):
        user = Worker.objects.filter(name=new_user.name)
        if user:
            raise UserAlreadyExists(user)
        worker = Worker.objects.create(**asdict(new_user))
        user.id = worker.id

    @classmethod
    def get_worker_shift(cls, worker_id: int, fromDate: datetime, toDate: datetime):
        workers_shifts = WorkerShift.objects.filter(
            id=worker_id, day__range=(fromDate, toDate))
        worker_shift_json = cls._serialize_object(workers_shifts)
        return json.dumps(worker_shift_json)

    @classmethod
    def create_worke_shift(cls, worker_shift: WorkerShift):
        WorkerShift.objects.create(vars(worker_shift))

    @classmethod
    def _serialize_object(cls, querySet: List[Worker]):
        serializedJson = serializers.serialize("json", querySet)
        jsonObj = json.loads(serializedJson)
        filteredJsonObj = [o['fields'] for o in jsonObj]
        return filteredJsonObj
