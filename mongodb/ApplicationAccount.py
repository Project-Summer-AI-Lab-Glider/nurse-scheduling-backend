from djongo import models


class ApplicationAccount(models.Model):
    client_id = models.CharField(max_length=100)
    worker_id = models.CharField(max_length=100)
    permissions = models.JSONField()
    objects = models.DjongoManager()
