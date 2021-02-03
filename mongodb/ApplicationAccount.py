from djongo import models


class ApplicationAccount(models.Model):
    client_id = models.CharField(max_length=100)
    session_id = models.CharField(max_length=300)
    worker_id = models.CharField(max_length=100)
    permissions = models.JSONField()
    refresh_token = models.CharField(max_length=100)
    objects = models.DjongoManager()
