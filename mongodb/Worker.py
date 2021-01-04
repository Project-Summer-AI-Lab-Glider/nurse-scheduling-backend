from djongo import models


class Worker(models.Model):
    worker_id = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)
    work_type = models.CharField(max_length=150)
    work_norm = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=150)
    objects = models.DjongoManager()
