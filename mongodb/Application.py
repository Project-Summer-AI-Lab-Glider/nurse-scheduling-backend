from djongo import models

class Application(models.Model):
    client_id = models.CharField()
    name = models.CharField()
    permissions = models.JSONField()
    objects = models.DjongoManager()