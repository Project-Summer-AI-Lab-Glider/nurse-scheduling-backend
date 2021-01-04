from djongo import models

class ApplicationAccount(models.Model):
    client_id = models.CharField(max_length=150)
    worker_id = models.CharField(max_length=150)
    permissions = models.JSONField()
    objects = models.DjongoManager()