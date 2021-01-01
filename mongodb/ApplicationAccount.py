from djongo import models

class ApplicationAccount(models.Model):
    client_id = models.CharField()
    worker_id = models.CharField()
    permissions = models.JSONField()
    objects = models.DjongoManager()