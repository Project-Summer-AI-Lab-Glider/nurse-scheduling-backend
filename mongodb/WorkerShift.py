from djongo import models

class WorkerShift(models.Model):
    code = models.CharField()
    objects = models.DjongoManager()