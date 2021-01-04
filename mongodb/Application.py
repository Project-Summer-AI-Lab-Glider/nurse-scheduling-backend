from djongo import models

class Application(models.Model):
    client_id = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    permissions = models.JSONField()
    objects = models.DjongoManager()