from djongo import models

class WorkerShift(models.Model):
    worker_id = models.CharField(max_length=150)
    fromHour = models.IntegerField()
    toHour = models.IntegerField()
    code = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    isWorking = models.BooleanField()
    day = models.DateField()
    objects = models.DjongoManager()