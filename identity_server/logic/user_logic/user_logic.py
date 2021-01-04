from mongodb.Worker import Worker
from mongodb.WorkerShift import WorkerShift
from django.core import serializers
import json
from dataclasses import dataclass


@dataclass
class User:
    name: str
    password: str


class UserLogic:
    def __init__(self) -> None:
        super().__init__()

    def get_contact(self, user_id):
        worker = Worker.objects.filter(worker_id=1).last()
        return json.dumps({
            'workerId': worker.worker_id,
            'name': worker.name,
            'phoneNumber': worker.phone_number,
        })

    def get_all_users(self):
        all_workers = Worker.objects.all()
        all_workers_json = self._serialize_object(all_workers)
        return json.dumps(all_workers_json)

    def get_user(self, user_id):
        worker = Worker.objects.filter(worker_id=user_id)
        worker_json = self._serialize_object(worker)
        return json.dumps(worker_json[0])

    def create_user(self, worker):
        Worker.objects.create(worker_id=worker.worker_id,
                              name=worker.name,
                              surname=worker.surname,
                              work_type=worker.work_type,
                              work_norm=worker.work_norm,
                              phone_number=worker.phone_number)

    def get_worker_shift(self, worker_id, fromDate, toDate):
        workers_shifts = WorkerShift.objects.filter(worker_id=worker_id)
        workers_shifts = workers_shifts.filter(day__range=(fromDate, toDate))
        worker_shift_json = self._serialize_object(workers_shifts)
        return json.dumps(worker_shift_json)

    def create_worke_shift(self, worker_shift):
        WorkerShift.objects.create(
            worker_id=worker_shift.worker_id,
            fromHour=worker_shift.fromHour,
            toHour=worker_shift.toHour,
            code=worker_shift.code,
            name=worker_shift.name,
            isWorking=worker_shift.isWorking,
            day=worker_shift.day
        )

    def _serialize_object(self, querySet):
        serializedJson = serializers.serialize("json", querySet)
        jsonObj = json.loads(serializedJson)
        filteredJsonObj = [o['fields'] for o in jsonObj]
        return filteredJsonObj
