from djongo import models

class Worker(models.Model):
    worker_id = models.CharField()
    name = models.CharField()
    surname = models.CharField()
    work_type = models.CharField()
    work_norm = models.CharField()
    phone_number = models.CharField()
    objects = models.DjongoManager()